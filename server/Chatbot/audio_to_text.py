import io
import spacy
import speech_recognition as sr
import re
import sqlite3
from rapidfuzz import process, fuzz
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import nltk
import os
from pathlib import Path
from ..Utils.svg_manipulator import main as make_svg
from ..Utils.loader import env_variables
from werkzeug.datastructures import FileStorage


nltk.download("stopwords", quiet=True)
nltk.download("punkt", quiet=True)
nltk.download("punkt_tab", quiet=True)


def audio_to_text(file_path: str) -> str:

    if not Path(file_path).is_file():
        return "Error: The specified audio file was not found."
    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(file_path) as source:
            print("Loading audio file...")
            audio_data = recognizer.record(source)
        print("Converting speech to text...")
        return recognizer.recognize_google(audio_data)
    except sr.UnknownValueError:
        return "Error: Speech in the audio file could not be understood."
    except sr.RequestError as e:
        return f"Error: Could not connect to Google Speech Recognition service: {e}"
    except Exception as e:
        return f"Unexpected error: {e}"


def extract_3_digit_numbers(text: str) -> list[int]:

    pattern_3_digit = r"\b\d{3}\b"
    result = [int(match) for match in re.findall(pattern_3_digit, text)[:2]]

    pattern_4_digit = r"\b2(\d{3})\b"
    match_4_digit = re.search(pattern_4_digit, text)
    if match_4_digit:

        result.insert(1, int(match_4_digit.group(1)))

    return result


def main(
    audio_file: FileStorage = None,
    audio_loc: str = None,
    db_path: str = env_variables.get("db_path"),
    audio_path: str = env_variables.get("audio_path"),
):

    db_path = Path(db_path).resolve()

    script_dir = Path(__file__).parent
    temp_audio_dir = audio_path

    if audio_loc:

        audio_path_resolved = Path(audio_loc)
        if not audio_path_resolved.is_absolute():
            audio_path_resolved = (script_dir / audio_path_resolved).resolve()
    else:

        if not audio_file:
            raise ValueError("No audio file provided.")
        audio_path_resolved = Path(temp_audio_dir) / audio_file.filename
        audio_file.save(audio_path_resolved)

    if not audio_path_resolved.exists():
        raise FileNotFoundError(f"Audio file not found: {audio_path_resolved}")

    query = audio_to_text(str(audio_path_resolved))
    print(query)

    if "Error" in query:
        return {"error": query}

    room_numbers = extract_3_digit_numbers(query)
    if len(room_numbers) == 0:
        return {"error": "Use at least 1 room number."}
    elif len(room_numbers) == 1:
        start = get_teacher_details_with_preprocessing(query, db_path)
        print("start: ", start)
        if "error" in start:
            return start
        start = start["Room_No"]
        end = str(room_numbers[0])
    else:
        start, end = map(str, room_numbers[:2])

    result = make_svg(start=start, end=end)

    return {"status": "SVG created successfully.", "result": result}


def preprocess_query(query):

    stop_words = set(stopwords.words("english"))

    words = word_tokenize(query)

    keywords = [word for word in words if word.lower() not in stop_words]

    return " ".join(keywords)


nlp = spacy.load("en_core_web_sm")


def extract_names(text):

    doc = nlp(text)
    names = [ent.text for ent in doc.ents if ent.label_ == "PERSON"]
    return "".join(names)


def get_teacher_details_with_preprocessing(teacher_name, db_path):

    try:

        teacher_name = re.sub(r"[^\w\s]", "", teacher_name)
        preprocessed_name_scypy = extract_names(teacher_name).lower()
        if not preprocessed_name_scypy or preprocessed_name_scypy in "kevin cabin":
            preprocessed_name_scypy = teacher_name.lower()
        preprocess_name_nltk = preprocess_query(teacher_name).lower()
        common_chars = "".join(
            [char for char in preprocessed_name_scypy if char in preprocess_name_nltk]
        )
        preprocessed_name = "".join(common_chars)

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        query = "SELECT name, cabin_no, room_no, phone_number FROM teachers"
        cursor.execute(query)
        records = cursor.fetchall()

        if not records:
            return {"error": "No data found in the database."}

        names = [row[0] for row in records]

        match, score, index = process.extractOne(
            preprocessed_name, names, scorer=fuzz.token_set_ratio
        )

        if score < 60:
            return {"error": "No close match found in the database."}

        matched_row = records[index]
        return {
            "Matched_Name": matched_row[0].title(),
            "Cabin": matched_row[1],
            "Room_No": matched_row[2],
            "Phone Number": matched_row[3],
        }
    except sqlite3.Error as e:
        return {"error": f"Database error: {e}"}
    finally:

        if conn:
            conn.close()


def open_audio_as_filestorage(file_path):

    try:

        prev = os.getcwd()
        script_dir = Path(__file__).parent
        os.chdir(script_dir)
        with open(file_path, "rb") as audio_file:

            file_content = audio_file.read()
            print(file_path.split("/")[-1])

            file_storage = FileStorage(io.BytesIO(file_content))
        os.chdir(prev)
        return file_storage
    except Exception as e:
        print(f"Error opening file: {e}")
        return None


if __name__ == "__main__":
    file = open_audio_as_filestorage("./temp_audio/temp.wav")
    print(main(audio_loc="./temp_audio/example_audio.wav"))
