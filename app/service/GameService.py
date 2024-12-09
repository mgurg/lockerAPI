import json
import secrets
from datetime import UTC, datetime
from time import perf_counter
from typing import Annotated
from uuid import UUID, uuid4

import httpx
from fastapi import Depends, HTTPException
from loguru import logger
from openai import AsyncOpenAI
from pydantic import BaseModel, IPvAnyAddress

from app.config import get_settings
from app.datbase.repository.AiGameRepo import AiGameRepo
from app.schemas.ai_game import CurrentPuzzleResponse, GameIntro, GameOutro, GameStart, PuzzleResponse, ReviewRequest

settings = get_settings()


class GameService:
    def __init__(
            self,
            ai_game_repo: Annotated[AiGameRepo, Depends()],
    ) -> None:
        self.ai_game_repo = ai_game_repo

    async def get_ai_response(self, prompt: str, response_model: BaseModel):
        start_time = perf_counter()
        try:
            client = AsyncOpenAI(api_key=settings.API_KEY_OPENAI)
            system_msg = """You are a creative escape room game master. Maintain story continuity and create engaging
             puzzles that connect logically to previous events. Each puzzle should base on facts or real persons histories
             but with different mechanics. Response in Polish language"""
            response = await client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": prompt},
                ],
                functions=[
                    {
                        "name": "generate_response",
                        "description": "Generate structured response for puzzle or ending",
                        "parameters": response_model.model_json_schema(),
                    }
                ],
                function_call={"name": "generate_response"},
                temperature=0.7,
            )

            function_args = response.choices[0].message.function_call.arguments
            return response_model.model_validate_json(function_args)
        except Exception as e:
            if "401" in str(e):
                print("Error: Unauthorized. Please verify that your API key is correct.")
                print("Visit https://platform.openai.com/account/api-keys to obtain a valid key.")
            else:
                print(f"An unexpected error occurred with the OpenAI API: {e}")
            return None
        finally:
            end_time = perf_counter()  # Stop high-resolution timer
            elapsed_time = end_time - start_time  # Calculate the elapsed time
            logger.info(f"⌛ Time taken for get_ai_response: {elapsed_time:.2f} seconds")

    async def start(self, setup: GameStart):

        ai_response: GameIntro = await self.get_ai_response(
            f"""Generate game introduction theme: {setup.theme}, details: {setup.description}, don't put riddles
             into response, try don't exceed 500 chars""",
            GameIntro)
        if not ai_response:
            raise HTTPException(status_code=500, detail="Failed to initialize game.")

        init_game_data = {
            "uuid": str(uuid4()),
            "token": secrets.token_hex(32),
            "theme": setup.theme,
            "description": setup.description,
            "difficulty": setup.difficulty,
            "category": setup.category,
            "occasion": setup.occasion,
            "email": setup.email,
            "intro": ai_response.intro,
            "state": "new",
            "current_puzzle": 0,
            "hints_remaining": 2,
            "wrong_answers": 0,
            "rating": 0,
            "remarks": None,
            "created_at": datetime.now(UTC),

        }

        db_ai_game = await self.ai_game_repo.create(**init_game_data)
        return db_ai_game

    async def fetch_geolocation(self, ip):
        if ip is not None:
            url = f"https://api.ipgeolocation.io/ipgeo?apiKey={settings.API_KEY_IPGEOLOCATION}&ip={ip}"
            location = None
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(url)
                    response.raise_for_status()  # Raise an error for HTTP errors
                    geo_data = response.json()
                    location = f"{geo_data['country_code3']}, {geo_data['city']}"
            except (httpx.RequestError, httpx.HTTPStatusError) as e:
                print(f"Error fetching geolocation for IP {ip}: {e}")
            except KeyError as e:
                print(f"Unexpected response structure for IP {ip}: Missing key {e}")
            except Exception as e:
                print(f"An unexpected error occurred for IP {ip}: {e}")

            return location

    async def intro(self, game_uuid: UUID, ip: IPvAnyAddress):
        db_game = await self.ai_game_repo.get_by_uuid(game_uuid)
        if not db_game or db_game.state != "new":
            raise HTTPException(status_code=404, detail="Game not found.")

        if db_game.ip is None and ip is not None:
            location = await self.fetch_geolocation(ip)
            logger.info(f"IP: {ip}, Location: {location}")
            # await self.ai_game_repo.update(db_game.id, **{"ip": ip, "location":location})
        return db_game

    async def generate_puzzle(self, game_uuid: UUID):
        db_game = await self.ai_game_repo.get_by_uuid(game_uuid)
        if not db_game or db_game.state != "new":
            raise HTTPException(status_code=404, detail="Game not found.")

        current_puzzle = db_game.current_puzzle

        if current_puzzle >= 4:
            raise HTTPException(status_code=404, detail="No more riddles")

        puzzle_counter: int = current_puzzle + 1
        last_puzzle = getattr(db_game, f"puzzle_{puzzle_counter}")
        if last_puzzle is not None:
            puzzle_response = json.loads(last_puzzle)
            new_puzzle = CurrentPuzzleResponse(**{
                "scenario": puzzle_response["scenario"],
                "base_hint": puzzle_response["base_hint"],
                "options": puzzle_response["options"],
                "correct": puzzle_response["correct"],
                "result": puzzle_response["result"],
                "wrong_feedback": puzzle_response["wrong_feedback"],
                "current_puzzle": puzzle_counter,
            })
            return new_puzzle

        previous_puzzles = [db_game.puzzle_1, db_game.puzzle_2, db_game.puzzle_3, db_game.puzzle_4]
        prev_puzzles_desc = []

        for old_puzzle in previous_puzzles:
            if old_puzzle is not None:
                puzzle = json.loads(old_puzzle)
                prev_puzzles_desc.append(puzzle["scenario"])
            prev_puzzles_desc.append(None)

        prev_puzzles_text = ",  ".join(
            f"{i + 1}: `{item}`" for i, item in enumerate(prev_puzzles_desc) if item is not None)

        puzzle_prompt = f"""Generate text puzzle number {puzzle_counter} of 4 for theme {db_game.theme} and
         description {db_game.description}, don't repeat those information in scenario. Scenario should return some subtle, useful
          tips to help solve riddles. There should be 3 options (answers) available,
          and only one correct. `wrong_feedback` numbers should correspond to `options` numbers.
          Don't repeat previous riddles ideas, create unique and various questions each time:
        {prev_puzzles_text}"""
        puzzle_response: PuzzleResponse = await self.get_ai_response(puzzle_prompt, PuzzleResponse)
        if not puzzle_response:
            raise HTTPException(status_code=500, detail="Failed to generate puzzle.")

        print(puzzle_response)
        puzzle_data = {
            f"puzzle_{puzzle_counter}": puzzle_response.model_dump_json()

        }

        print(puzzle_data)
        await self.ai_game_repo.update(db_game.id, **puzzle_data)

        new_puzzle = CurrentPuzzleResponse(**{
            "scenario": puzzle_response.scenario,
            "base_hint": puzzle_response.base_hint,
            "options": puzzle_response.options,
            "correct": puzzle_response.correct,
            "result": puzzle_response.result,
            "wrong_feedback": puzzle_response.wrong_feedback,
            "current_puzzle": puzzle_counter,
        })
        return new_puzzle

    async def answer(self, game_uuid: UUID, choice: int):
        db_game = await self.ai_game_repo.get_by_uuid(game_uuid)
        if not db_game or db_game.state != "new":
            raise HTTPException(status_code=404, detail="Game not found or not running.")

        current_puzzle = db_game.current_puzzle
        puzzle_counter: int = current_puzzle + 1

        puzzle = getattr(db_game, f"puzzle_{puzzle_counter}")
        puzzle_json = json.loads(puzzle)
        if choice == puzzle_json["correct"]:
            await self.ai_game_repo.update(db_game.id, **{"current_puzzle": db_game.current_puzzle + 1})
            return {"result": puzzle_json["result"], "correct": True}
        else:
            wrong_answers = db_game.wrong_answers + 1
            await self.ai_game_repo.update(db_game.id, **{"wrong_answers": wrong_answers})
            if wrong_answers >= 5:
                await self.ai_game_repo.update(db_game.id, **{"wrong_answers": wrong_answers, "state": "trapped"})
                return {"result": "You are trapped!", "correct": False}

            # Access feedback directly from the dictionaries
        feedback = next(
            (item["feedback"] for item in puzzle_json["wrong_feedback"] if item["number"] == choice),
            "Incorrect choice."
        )
        return {"result": feedback, "correct": False}

    async def ending(self, game_uuid: UUID):
        db_game = await self.ai_game_repo.get_by_uuid(game_uuid)
        if not db_game or db_game.state != "new":
            raise HTTPException(status_code=404, detail="Game not found or not running.")

        previous_puzzles = [db_game.puzzle_1, db_game.puzzle_2, db_game.puzzle_3, db_game.puzzle_4]
        prev_puzzles_desc = []

        for old_puzzle in previous_puzzles:
            if old_puzzle is not None:
                puzzle = json.loads(old_puzzle)
                prev_puzzles_desc.append(puzzle["scenario"])
            prev_puzzles_desc.append(None)

        prev_puzzles_text = ",  ".join(
            f"{i + 1}: `{item}`" for i, item in enumerate(prev_puzzles_desc) if item is not None)

        ending_prompt = f"""Generate an ending based on initial intro: `{db_game.intro}` and
         progress: {prev_puzzles_text} keep it below 300 chars. It should contains unexpected twist"""
        ending = await self.get_ai_response(ending_prompt, GameOutro)

        return ending

    async def review(self, game_uuid: UUID, review: ReviewRequest) -> None:
        db_game = await self.ai_game_repo.get_by_uuid(game_uuid)
        if not db_game or db_game.state != "new":
            raise HTTPException(status_code=404, detail="Game not found or not running.")

        await self.ai_game_repo.update(db_game.id, **{"rating": review.score, "remarks": review.text})

        return None
