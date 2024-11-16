import asyncio
from io import BytesIO
from typing import Union

from PIL import Image, ImageDraw, ImageFont
from colorthief import ColorThief
import aiohttp
import discord
from concurrent.futures import ThreadPoolExecutor

from bot.utils.tools import gen_id


class MusicCard:
    def __init__(self, image_link, title, artists, duration, added_by):
        self._image_link = image_link
        self._title = self._calculate_text(title)
        self._artists = self._calculate_authors(artists)
        self._duration = duration
        self._added_by = added_by

    @staticmethod
    async def _download_image(url):
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                return await response.read()

    @staticmethod
    def _IMGtoFILE(IMG: Image) -> Union[discord.File, BytesIO]:
        uniq_id = gen_id()
        with BytesIO() as image_binary:
            IMG.save(image_binary, "PNG")
            image_binary.seek(0)
            return discord.File(fp=image_binary, filename=f"{uniq_id}.png")

    @staticmethod
    def _process_image(image_data):
        main_image = Image.open(BytesIO(image_data)).convert("RGBA")
        main_image = main_image.resize((200, 200))

        color_thief = ColorThief(BytesIO(image_data))
        dominant_color = color_thief.get_color(quality=10)
        return main_image, dominant_color

    @staticmethod
    def _create_diagonal_gradient(width, height, color1, color2):
        base = Image.new("RGBA", (width, height), color1)
        top = Image.new("RGBA", (width, height), color2)

        mask = Image.new("L", (width, height))
        ImageDraw.Draw(mask)

        for i in range(width):
            for j in range(height):
                mask.putpixel((i, j), int(255 * (i + j) / (width + height)))

        gradient = Image.composite(base, top, mask)
        return gradient

    @staticmethod
    def _get_text_color(background_color):
        r, g, b = background_color
        brightness = (r * 299 + g * 587 + b * 114) / 1000
        return (255, 255, 255) if brightness < 128 else (0, 0, 0)

    @staticmethod
    def _add_rounded_corners(image, radius):
        mask = Image.new("L", image.size, 0)
        draw = ImageDraw.Draw(mask)
        draw.rounded_rectangle((0, 0, mask.width, mask.height), radius, fill=255)
        rounded_image = Image.new("RGBA", image.size, (0, 0, 0, 0))
        rounded_image.paste(image, (0, 0), mask)
        return rounded_image

    @staticmethod
    def _calculate_text(text):
        # Задаем вес символов
        weight_upper = 3
        weight_lower = 2
        weight_space = 1
        weight_digit = 2

        max_weight = 39
        current_weight = 0
        result = ""

        for char in text:
            if char.isupper():
                current_weight += weight_upper
            elif char.islower():
                current_weight += weight_lower
            elif char.isspace():
                current_weight += weight_space
            elif char.isdigit():
                current_weight += weight_digit
            else:
                current_weight += weight_lower

            if current_weight > max_weight:
                break

            result += char

        if len(result) > 3 and current_weight > max_weight:
            result = result[:-3] + "..."

        return result

    @staticmethod
    def _calculate_authors(authors):
        # Задаем вес символов
        weight_upper = 3
        weight_lower = 2
        weight_space = 1
        weight_digit = 2

        max_weight = 59

        def calculate_weight(text):
            weight = 0
            for char in text:
                if char.isupper():
                    weight += weight_upper
                elif char.islower():
                    weight += weight_lower
                elif char.isspace():
                    weight += weight_space
                elif char.isdigit():
                    weight += weight_digit
                else:
                    weight += weight_lower
            return weight

        authors_list = authors.split(", ")
        authors_len_old = len(authors_list)

        while True:
            current_weight = calculate_weight(", ".join(authors_list))
            if current_weight <= max_weight:
                break
            if len(authors_list) > 1:
                authors_list.pop()
            else:
                break

        authors_new = len(authors_list)

        if authors_len_old > authors_new:
            authors_n = ", ".join(authors_list) + "..."
            return authors_n

        return ", ".join(authors_list)

    @staticmethod
    def _make_color_brighter(color, delta=10, make="+"):
        r, g, b = color
        if make == "+":
            r = min(r + delta, 255)
            g = min(g + delta, 255)
            b = min(b + delta, 255)
        else:
            r = max(r - delta, 0)
            g = max(g - delta, 0)
            b = max(b - delta, 0)
        return r, g, b

    def _create_music_card_image(self, image_data):
        main_image, dominant_color = self._process_image(image_data)
        main_image = self._add_rounded_corners(main_image, radius=15)

        color1, color2 = self._make_color_brighter(dominant_color, 20), dominant_color

        card_width, card_height = 800, 300
        gradient = self._create_diagonal_gradient(card_width, card_height, color1, color2)

        card = Image.new("RGBA", (card_width, card_height))
        card.paste(gradient, (0, 0))

        image_x = (card_width - main_image.width) // 10
        image_y = (card_height - main_image.height) // 2
        card.paste(main_image, (image_x, image_y), main_image)

        font_path = "gothampro_bold.ttf"
        player_font = ImageFont.truetype(font_path, 28)
        title_font = ImageFont.truetype(font_path, 42)
        info_font = ImageFont.truetype(font_path, 17)

        title_color = self._get_text_color(dominant_color)
        if title_color == (0, 0, 0):
            other_color = self._make_color_brighter(title_color, 55, make="+")
        else:
            other_color = self._make_color_brighter(title_color, 55, make="-")

        title_color = title_color + (220,)
        other_color = other_color + (220,)

        text_layer = Image.new("RGBA", card.size, (255, 255, 255, 0))
        text_draw = ImageDraw.Draw(text_layer)

        text_x = image_x + main_image.width + 20
        text_draw.text((text_x, 55), "Сейчас играет", font=player_font, fill=other_color)
        text_draw.text((text_x, 100), self._title, font=title_font, fill=title_color)
        text_draw.text((text_x, 145), self._artists, font=player_font, fill=other_color)
        text_draw.text((text_x, 205), f"Длительность: {self._duration}", font=info_font, fill=other_color)
        text_draw.text((text_x, 225), f"Добавил: {self._added_by}", font=info_font, fill=other_color)

        card = Image.alpha_composite(card, text_layer)
        return self._IMGtoFILE(card), dominant_color

    async def create_music_card(self):
        image_data = await self._download_image(self._image_link)
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as pool:
            file, dominant_color = await loop.run_in_executor(pool, self._create_music_card_image, image_data)
        return file, dominant_color
