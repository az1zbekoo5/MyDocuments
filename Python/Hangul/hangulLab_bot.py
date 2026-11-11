import random
import json
import os
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    ContextTypes,
    filters
)

TOKEN = "8200068915:AAEAwv8oq5xKTQnMwUfHVVCZ0fcIvcN5_ZM"

ASK_LANG, MAIN, UPDATE_TOPIC, UPDATE_WORDS, UPDATE_ACTION = range(5)
# ======================================================
# 1. LOAD/SAVE VOCABULARY
# ======================================================
VOCAB_FILE = "vocab.json"

def load_vocab():
    if not os.path.exists(VOCAB_FILE):
        return{}
    with open(VOCAB_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)
    
def save_vocab(vocab):
    with open(VOCAB_FILE, 'w', encoding='utf-8') as f:
        json.dump(vocab, f, ensure_ascii=False, indent=4)

# Global vocab

def rebuild_reverse():
    KOREAN_VOCAB_REVERSE.clear()
    for topic, words in KOREAN_VOCAB.items():
        KOREAN_VOCAB_REVERSE[topic] = {v.lower(): k for k, v in words.items()}

KOREAN_VOCAB = load_vocab()
KOREAN_VOCAB_REVERSE = {}
rebuild_reverse()

# ======================================================
# 2. TRANSLATIONS
# ======================================================

TRANSLATIONS = {
    'en': {
        'welcome': (
            "👋 Welcome {name}!\n\n"
            "📖 Learn Korean step by step:\n"
            "• Hangul (Korean alphabet)\n"
            "• Korean numbers\n"
            "• Vocabulary by topics\n\n"
            "**Commands:**\n"
            "👉 /study — Study lists and vocabulary\n"
            "👉 /practice — Practice with quizzes\n"
            "👉 /lang — Change bot language\n"
            "👉 /score — View your progress\n"
            "👉 /help — How to use the bot\n"
            "👉 /stop — Stop current quiz\n\n"
            "Let's start learning Korean together! 🚀"),

        'choose_lang': "🌐 Please choose your language:",
        'lang_en': "🇬🇧 English",
        'lang_ru': "🇷🇺 Русский",
        'lang_ko': "🇰🇷 한국어",
        'lang_uz': "🇺🇿 O'zbek",

        'help': (
            "**📚 How to Use This Bot**\n\n"
            "This bot helps you learn **Korean numbers and vocabulary** through study lists and interactive quizzes.\n\n"

            "**🔹 Main Commands**\n"
            "📘 /study — Browse learning materials\n"
            "  • Korean alphabet\n"
            "  • Korean numbers\n"
            "  • Vocabulary grouped by topics\n\n"

            "🎮 /practice — Start a quiz\n"
            "  • Numbers or vocabulary\n"
            "  • Choose a topic (for words)\n"
            "  • Choose translation direction\n"
            "  • Choose difficulty (for numbers)\n\n"

            "🌐 /lang — Change the bot interface language\n"
            "📊 /score — View your quiz statistics and accuracy\n"
            "🛑 /stop — Stop the current quiz at any time\n\n"

            "**🧠 Quiz System**\n"
            "• Instant feedback after each answer\n"
            "• Automatic level increase when you perform well\n"
            "• Helpful tips if you make repeated mistakes\n\n"

            "Your progress is saved automatically. Keep practicing and improve step by step! 🚀"
        ),
        'study_sino': "📘 *Sino Numbers*\n\n",
        'study_native': "\n📗 *Native Numbers*\n\n",
        'study_alphabet': "📜 Korean Alphabet\n\n",
        'study_words': "**🇰🇷 Korean Vocabulary**\n\n", 

        'study_ready': "👉 You can now use /play to start a 🎮 quiz.",

        'play_choose_mode': "🎯 Choose your quiz mode:",
        'mode_num_to_target': "🔢 Number ➜ 🔠Word",
        'mode_target_to_num': "🔠 Word ➜ 🔢 Number",

        'kore_to_eng': "🇰🇷 Korean ➜ 󠁧󠁢🇬🇧 English",
        'eng_to_kore': "🇬🇧 English ➜ 🇰🇷 Korean",

        'study_choose_mode': "🎯 Choose your study mode:",
        'korean_alp': "🔠 Korean Alphabet",
        'korean_num': "🔢 Korean Number",
        'korean_word': "🔠 Korean Words",

        'play_num_mode': "🔢 Number",
        'play_word_mode': "🔠 Word",

        'choose_level': "Now choose your difficulty level:",
        'level_easy': "🟢 Easy (1–10)",
        'level_medium': "🟡 Medium (1–1000)",
        'level_hard': "🔴 Hard (1–999999)",

        'game_start': "*{level}* difficulty\nLet's start!",
        'question_num_to_target': "🔢 ➜ 🔠\n\nWhat is '{num}' in Korean?",
        'question_target_to_num': "🔠 ➜ 🔢\n\nWhat number is '{word}'?",


        'topic_list': "Choose a topic for word quiz:",
        'question_eng_to_kor': "🇬🇧 ➜ 🇰🇷\n\nWhat is '{eng}' in Korean?",
        'question_kor_to_eng': "🇰🇷 ➜ 🇬🇧\n\nWhat is '{kor}' in English?",



        'score_title': "📊 *Your Progress*\n\n",
        'score_correct': "✅ Correct: {correct}\n",
        'score_wrong': "❌ Wrong: {wrong}\n",
        'score_streak': "🔥 Streak: {streak}\n",
        'score_accuracy': "🎯 Accuracy: {acc:.1f}%",
        'positive': ["🎉 Perfect!", "✅ Exactly right!", "👏 Awesome work!", "🔥 Great memory!", "😎 Well done!", "🥳 Nice job!"],
        'negative': ["❌ Oops! Try again!", "😅 Not quite!", "📘 Study a bit more!", "🤔 Close,but not right!", "🧩 You'll get it next time!"],

        'correct': "✅ Correct",
        'wrong': "❌ Wrong",

        'correct_answer': "Correct: {answer}",
        'tip': "💡 Tip: Try saying the numbers aloud!",
        'level_up_easy': "🚀 Leveled up to Medium!",
        'level_up_medium': "🚀 Leveled up to Hard!",
        'stop': "🛑 Game stopped. Type /play to start again anytime!",

        'update_intro': "📝 Add new words to your vocabulary!\n\n"
                        "First, enter the topic name (e.g., Food, Travel, General):",
        'update_words': "Now send words in format:\nenglish = korean\n(one per line)\n\nExample:\ncat = 고양이\ndog = 개",
        'update_success': "✅ {count} words added to '{topic}' topic!",
        'update_no_words': "❌ No valid words found.",

        'add_new_word': "Add new words",
        'edit_exist': "Edit existing",
        'delete_top': "Delete topic",

        'already_exist': "Topic '{topic}' already exists. What would you like to do? 👇",
        'expired_ses': "Session expired. Please run /update again.",

        'edit_number': "Reply with the number of the word you want to edit.",
        'topic_del': "Topic '{topic}' deleted. ",
        'updated_word': "Updated: {eng} → {new_kor}",

        'nkorean_translation': "Current: {eng} → {current_kor}\n\n Send the new Korean translation:" ,
        'num_error': "Invalid number. Try again or /stop.",
        'empty_topic': "No words in this topic yet.",

        'study_topic': "🎯 Choose a topic:"
    },
    'ru': {
        'welcome': (
            "👋 Добро пожаловать, {name}!\n\n"
            "📖 Изучайте корейский шаг за шагом:\n"
            "• Корейский алфавит (ханыль)\n"
            "• Корейские числа\n"
            "• Слова по темам\n\n"
            "**Команды:**\n"
            "👉 /study — Учебные материалы и слова\n"
            "👉 /practice — Практика в формате викторины\n"
            "👉 /lang — Сменить язык бота\n"
            "👉 /score — Посмотреть прогресс\n"
            "👉 /help — Как пользоваться ботом\n"
            "👉 /stop — Остановить текущую игру\n\n"
            "Начнём изучать корейский вместе! 🚀"

        ),

        'choose_lang': "🌐 Пожалуйста, выберите язык:",
        'lang_en': "🇬🇧 Английский",
        'lang_ru': "🇷🇺 Русский",
        'lang_ko': "🇰🇷 Корейский",
        'lang_uz': "🇺🇿 Узбекский",
        'help': (
            "**📚 Как пользоваться ботом**\n\n"
            "Этот бот помогает изучать **корейские числа и лексику** с помощью списков и интерактивных викторин.\n\n"
            "**🔹 Основные команды**\n"
            "📘 /study — Учебные материалы\n"
            "  • Корейский алфавит\n"
            "  • Корейские числа\n"
            "  • Слова по темам\n\n"
            "🎮 /practice — Начать викторину\n"
            "  • Числа или слова\n"
            "  • Выбор темы\n"
            "  • Направление перевода\n"
            "  • Уровень сложности\n\n"
            "🌐 /lang — Сменить язык интерфейса\n"
            "📊 /score — Посмотреть статистику\n"
            "🛑 /stop — Остановить викторину\n\n"
            "Ваш прогресс сохраняется автоматически. Удачи! 🚀"
        ),

        'study_sino': "📘 *Сино-корейские числа*\n\n",
        'study_native': "\n📗 *Коренные корейские числа*\n\n",
        'study_alphabet': "📜 Корейский алфавит\n\n",
        'study_words': "**🇰🇷 Корейская лексика**\n\n",

        'study_ready': "👉 Теперь вы можете использовать /play, чтобы начать викторину 🎮",

        'play_choose_mode': "🎯 Выберите режим викторины:",
        'mode_num_to_target': "🔢 Число ➜ 🔠 Слово",
        'mode_target_to_num': "🔠 Слово ➜ 🔢 Число",

        'kore_to_eng': "🇰🇷 Корейский ➜ 🇬🇧 Английский",
        'eng_to_kore': "🇬🇧 Английский ➜ 🇰🇷 Корейский",

        'study_choose_mode': "🎯 Выберите режим обучения:",
        'korean_alp': "🔠 Корейский алфавит",
        'korean_num': "🔢 Корейские числа",
        'korean_word': "🔠 Корейские слова",

        'play_num_mode': "🔢 Числа",
        'play_word_mode': "🔠 Слова",

        'choose_level': "Выберите уровень сложности:",
        'level_easy': "🟢 Легко (1–10)",
        'level_medium': "🟡 Средне (1–1000)",
        'level_hard': "🔴 Сложно (1–999999)",

        'game_start': "*Уровень: {level}*\nНачинаем!",
        'question_num_to_target': "🔢 ➜ 🔠\n\nКак будет '{num}' по-корейски?",
        'question_target_to_num': "🔠 ➜ 🔢\n\nКакое число означает '{word}'?",

        'topic_list': "Выберите тему для викторины:",
        'question_eng_to_kor': "🇬🇧 ➜ 🇰🇷\n\nКак '{eng}' по-корейски?",
        'question_kor_to_eng': "🇰🇷 ➜ 🇬🇧\n\nЧто означает '{kor}' по-английски?",

        'score_title': "📊 *Ваш прогресс*\n\n",
        'score_correct': "✅ Верно: {correct}\n",
        'score_wrong': "❌ Неверно: {wrong}\n",
        'score_streak': "🔥 Серия: {streak}\n",
        'score_accuracy': "🎯 Точность: {acc:.1f}%",

        'positive': ["🎉 Отлично!", "✅ Правильно!", "👏 Отличная работа!", "🔥 Прекрасная память!"],
        'negative': ["❌ Неправильно!", "😅 Почти!", "📘 Нужно повторить!"],

        'correct': "✅ Правильно",
        'wrong': "❌ Неправильно",

        'correct_answer': "Правильный ответ: {answer}",
        'tip': "💡 Совет: попробуйте произносить вслух!",
        'level_up_easy': "🚀 Уровень повышен до среднего!",
        'level_up_medium': "🚀 Уровень повышен до сложного!",
        'stop': "🛑 Игра остановлена. Напишите /play, чтобы начать снова.",

        'update_intro': "📝 Добавление новых слов\n\nВведите название темы:",
        'update_words': "Отправьте слова в формате:\nenglish = korean\n\nПример:\ncat = 고양이",
        'update_success': "✅ Добавлено слов: {count} (тема: {topic})",
        'update_no_words': "❌ Не найдено подходящих слов.",

        'add_new_word': "Добавить слова",
        'edit_exist': "Редактировать",
        'delete_top': "Удалить тему",

        'already_exist': "Тема '{topic}' уже существует. Что сделать?",
        'expired_ses': "Сессия истекла. Запустите /update снова.",

        'edit_number': "Введите номер слова для редактирования.",
        'topic_del': "Тема '{topic}' удалена.",
        'updated_word': "Обновлено: {eng} → {new_kor}",

        'nkorean_translation': "Текущее: {eng} → {current_kor}\n\nВведите новый перевод:",
        'num_error': "Неверный номер. Попробуйте снова.",
        'empty_topic': "В этой теме пока нет слов.",
        'study_topic': "🎯 Выберите тему:"
    },
    'ko': {
        'welcome': (
            "👋 {name}님, 환영합니다!\n\n"
            "📖 한국어를 단계별로 학습해 보세요:\n"
            "• 한글 (한국어 알파벳)\n"
            "• 한국어 숫자\n"
            "• 주제별 어휘\n\n"
            "**명령어:**\n"
            "👉 /study — 학습 자료 보기\n"
            "👉 /practice — 퀴즈로 연습하기\n"
            "👉 /lang — 봇 언어 변경\n"
            "👉 /score — 학습 진행 상황\n"
            "👉 /help — 사용 방법 안내\n"
            "👉 /stop — 현재 퀴즈 종료\n\n"
            "함께 즐겁게 한국어를 배워요! 🚀"

        ),

        'choose_lang': "🌐 언어를 선택하세요:",
        'lang_en': "🇬🇧 영어",
        'lang_ru': "🇷🇺 러시아어",
        'lang_ko': "🇰🇷 한국어",
        'lang_uz': "🇺🇿 우즈베크어",

        'help': (
            "**📚 사용 방법**\n\n"
            "이 봇은 **한국어 숫자와 단어**를 학습하고 퀴즈로 연습할 수 있도록 도와줍니다.\n\n"

            "**🔹 주요 명령어**\n"
            "📘 /study — 학습 자료 보기\n"
            "  • 한글\n"
            "  • 한국어 숫자\n"
            "  • 주제별 단어\n\n"

            "🎮 /practice — 퀴즈 시작\n"
            "  • 숫자 또는 단어\n"
            "  • 단어 주제 선택\n"
            "  • 번역 방향 선택\n"
            "  • 숫자 난이도 선택\n\n"

            "🌐 /lang — 봇 언어 변경\n"
            "📊 /score — 퀴즈 통계 확인\n"
            "🛑 /stop — 언제든지 퀴즈 중지\n\n"

            "**🧠 퀴즈 시스템**\n"
            "• 각 답변 후 즉시 피드백 제공\n"
            "• 성과가 좋으면 자동으로 난이도 상승\n"
            "• 반복 실수 시 도움 팁 제공\n\n"

            "학습 진행 상황은 자동 저장됩니다. 꾸준히 연습하세요! 🚀"
        ),

        'study_sino': "📘 *한자어 숫자*\n\n",
        'study_native': "\n📗 *고유어 숫자*\n\n",
        'study_alphabet': "📜 한글\n\n",
        'study_words': "**🇰🇷 한국어 단어**\n\n",

        'study_ready': "👉 이제 /play 를 사용해 🎮 퀴즈를 시작할 수 있습니다.",

        'play_choose_mode': "🎯 퀴즈 모드를 선택하세요:",
        'mode_num_to_target': "🔢 숫자 ➜ 🔠 단어",
        'mode_target_to_num': "🔠 단어 ➜ 🔢 숫자",

        'kore_to_eng': "🇰🇷 한국어 ➜ 🇬🇧 영어",
        'eng_to_kore': "🇬🇧 영어 ➜ 🇰🇷 한국어",

        'study_choose_mode': "🎯 학습 모드를 선택하세요:",
        'korean_alp': "🔠 한글",
        'korean_num': "🔢 한국어 숫자",
        'korean_word': "🔠 한국어 단어",

        'play_num_mode': "🔢 숫자",
        'play_word_mode': "🔠 단어",

        'choose_level': "난이도를 선택하세요:",
        'level_easy': "🟢 쉬움 (1–10)",
        'level_medium': "🟡 보통 (1–1000)",
        'level_hard': "🔴 어려움 (1–999999)",

        'game_start': "*{level}* 난이도\n시작합니다!",
        'question_num_to_target': "🔢 ➜ 🔠\n\n'{num}' 은(는) 한국어로 무엇인가요?",
        'question_target_to_num': "🔠 ➜ 🔢\n\n'{word}' 은(는) 어떤 숫자인가요?",

        'topic_list': "단어 퀴즈 주제를 선택하세요:",
        'question_eng_to_kor': "🇬🇧 ➜ 🇰🇷\n\n'{eng}' 의 한국어는 무엇인가요?",
        'question_kor_to_eng': "🇰🇷 ➜ 🇬🇧\n\n'{kor}' 의 영어 뜻은 무엇인가요?",

        'score_title': "📊 *나의 학습 기록*\n\n",
        'score_correct': "✅ 정답: {correct}\n",
        'score_wrong': "❌ 오답: {wrong}\n",
        'score_streak': "🔥 연속 정답: {streak}\n",
        'score_accuracy': "🎯 정확도: {acc:.1f}%",

        'positive': ["🎉 완벽해요!", "✅ 정답입니다!", "👏 훌륭해요!", "🔥 기억력이 대단해요!", "😎 잘했어요!", "🥳 멋져요!"],
        'negative': ["❌ 틀렸어요!", "😅 거의 맞았어요!", "📘 조금 더 공부해요!", "🤔 아쉬워요!", "🧩 다음엔 맞출 수 있어요!"],

        'correct': "✅ 정답입니다",
        'wrong': "❌ 틀렸어요",

        'correct_answer': "정답: {answer}",
        'tip': "💡 팁: 숫자를 소리 내어 말해보세요!",
        'level_up_easy': "🚀 보통 난이도로 올라갔어요!",
        'level_up_medium': "🚀 어려움 난이도로 올라갔어요!",
        'stop': "🛑 퀴즈가 중지되었습니다. 언제든 /play 로 다시 시작하세요!",

        'update_intro': (
            "📝 새 단어 추가하기!\n\n"
            "먼저 주제 이름을 입력하세요 (예: Food, Travel, General):"
        ),
        'update_words': (
            "다음 형식으로 단어를 보내세요:\n"
            "english = korean\n"
            "(한 줄에 하나)\n\n"
            "예시:\ncat = 고양이\ndog = 개"
        ),
        'update_success': "✅ '{topic}' 주제에 {count}개의 단어가 추가되었습니다!",
        'update_no_words': "❌ 유효한 단어를 찾지 못했습니다.",

        'add_new_word': "새 단어 추가",
        'edit_exist': "기존 단어 수정",
        'delete_top': "주제 삭제",

        'already_exist': "주제 '{topic}' 가 이미 존재합니다. 무엇을 하시겠어요? 👇",
        'expired_ses': "세션이 만료되었습니다. /update 를 다시 실행하세요.",

        'edit_number': "수정할 단어의 번호를 입력하세요.",
        'topic_del': "주제 '{topic}' 가 삭제되었습니다.",
        'updated_word': "수정됨: {eng} → {new_kor}",

        'nkorean_translation': "현재: {eng} → {current_kor}\n\n새 한국어 번역을 입력하세요:",
        'num_error': "잘못된 번호입니다. 다시 시도하거나 /stop 을 입력하세요.",
        'empty_topic': "이 주제에는 아직 단어가 없습니다.",

        'study_topic': "🎯 학습할 주제를 선택하세요:"
    },
    'uz': {
        'welcome': (
            "👋 Xush kelibsiz, {name}!\n\n"
            "📖 Koreys tilini bosqichma-bosqich o‘rganing:\n"
            "• Hangul (koreys alifbosi)\n"
            "• Koreyscha sonlar\n"
            "• Mavzular bo'yicha lug'at\n\n"
            "**Buyruqlar:**\n"
            "👉 /study — O'rganish materiallari\n"
            "👉 /practice — Test orqali mashq qilish\n"
            "👉 /lang — Bot tilini o'zgartirish\n"
            "👉 /score — Natijalar va statistika\n"
            "👉 /help — Foydalanish bo'yicha yordam\n"
            "👉 /stop — Joriy testni to'xtatish\n\n"
            "Keling, koreys tilini birga o'rganamiz! 🚀"

        ),
    
        'choose_lang': "🌐 Tilni tanlang:",
        'lang_en': "🇬🇧 Inglizcha",
        'lang_ru': "🇷🇺 Ruscha",
        'lang_ko': "🇰🇷 Koreyscha",
        'lang_uz': "🇺🇿 O‘zbekcha",
    
        'help': (
            "**📚 Botdan qanday foydalaniladi**\n\n"
            "Bu bot **koreyscha sonlar va so‘zlarni** ro‘yxatlar va interaktiv testlar orqali o‘rganishga yordam beradi.\n\n"
    
            "**🔹 Asosiy buyruqlar**\n"
            "📘 /study — O‘quv materiallari\n"
            "  • Koreys alifbosi\n"
            "  • Koreyscha sonlar\n"
            "  • Mavzular bo‘yicha so‘zlar\n\n"
    
            "🎮 /practice — Testni boshlash\n"
            "  • Sonlar yoki so‘zlar\n"
            "  • So‘z mavzusini tanlash\n"
            "  • Tarjima yo‘nalishi\n"
            "  • Sonlar uchun daraja\n\n"
    
            "🌐 /lang — Bot tilini o‘zgartirish\n"
            "📊 /score — Statistikani ko‘rish\n"
            "🛑 /stop — Testni istalgan paytda to‘xtatish\n\n"
    
            "**🧠 Test tizimi**\n"
            "• Har bir javobdan so‘ng darhol natija\n"
            "• Yaxshi natija ko‘rsatsangiz daraja oshadi\n"
            "• Takroriy xatolarda foydali maslahatlar\n\n"
    
            "Natijalar avtomatik saqlanadi. Mashq qilishda davom eting! 🚀"
        ),
    
        'study_sino': "📘 *Sino-koreys sonlari*\n\n",
        'study_native': "\n📗 *Asl koreys sonlari*\n\n",
        'study_alphabet': "📜 Koreys alifbosi\n\n",
        'study_words': "**🇰🇷 Koreyscha so‘zlar**\n\n",
    
        'study_ready': "👉 Endi 🎮 testni boshlash uchun /play buyrug‘idan foydalaning.",
    
        'play_choose_mode': "🎯 Test turini tanlang:",
        'mode_num_to_target': "🔢 Son ➜ 🔠 So‘z",
        'mode_target_to_num': "🔠 So‘z ➜ 🔢 Son",
    
        'kore_to_eng': "🇰🇷 Koreyscha ➜ 🇬🇧 Inglizcha",
        'eng_to_kore': "🇬🇧 Inglizcha ➜ 🇰🇷 Koreyscha",
    
        'study_choose_mode': "🎯 O‘rganish turini tanlang:",
        'korean_alp': "🔠 Koreys alifbosi",
        'korean_num': "🔢 Koreyscha sonlar",
        'korean_word': "🔠 Koreyscha so‘zlar",
    
        'play_num_mode': "🔢 Sonlar",
        'play_word_mode': "🔠 So‘zlar",
    
        'choose_level': "Darajani tanlang:",
        'level_easy': "🟢 Oson (1–10)",
        'level_medium': "🟡 O‘rtacha (1–1000)",
        'level_hard': "🔴 Qiyin (1–999999)",
    
        'game_start': "*{level}* daraja\nBoshladik!",
        'question_num_to_target': "🔢 ➜ 🔠\n\n'{num}' koreys tilida qanday aytiladi?",
        'question_target_to_num': "🔠 ➜ 🔢\n\n'{word}' qaysi songa teng?",
    
        'topic_list': "So‘zlar testi uchun mavzuni tanlang:",
        'question_eng_to_kor': "🇬🇧 ➜ 🇰🇷\n\n'{eng}' koreys tilida nima?",
        'question_kor_to_eng': "🇰🇷 ➜ 🇬🇧\n\n'{kor}' ingliz tilida nima?",
    
        'score_title': "📊 *Sizning natijalaringiz*\n\n",
        'score_correct': "✅ To‘g‘ri: {correct}\n",
        'score_wrong': "❌ Noto‘g‘ri: {wrong}\n",
        'score_streak': "🔥 Ketma-ket: {streak}\n",
        'score_accuracy': "🎯 Aniqlik: {acc:.1f}%",
    
        'positive': ["🎉 Zo‘r!", "✅ To‘g‘ri!", "👏 Ajoyib!", "🔥 Juda yaxshi!", "😎 Barakalla!", "🥳 Zo‘r ish!"],
        'negative': ["❌ Noto‘g‘ri!", "😅 Sal qoldi!", "📘 Yana mashq qiling!", "🤔 Yaqin edi!", "🧩 Keyingi safar bo‘ladi!"],

        'correct': "✅ To‘g‘ri",
        'wrong': "❌ Noto‘g‘ri",

        'correct_answer': "To‘g‘ri javob: {answer}",
        'tip': "💡 Maslahat: sonlarni ovoz chiqarib ayting!",
        'level_up_easy': "🚀 O‘rtacha darajaga o‘tdingiz!",
        'level_up_medium': "🚀 Qiyin darajaga o‘tdingiz!",
        'stop': "🛑 Test to‘xtatildi. Istalgan vaqtda /play bilan davom eting!",
    
        'update_intro': (
            "📝 Yangi so‘zlar qo‘shish!\n\n"
            "Avval mavzu nomini kiriting (masalan: Food, Travel, General):"
        ),
        'update_words': (
            "So‘zlarni quyidagi formatda yuboring:\n"
            "english = korean\n"
            "(har qatorda bittadan)\n\n"
            "Misol:\ncat = 고양이\ndog = 개"
        ),
        'update_success': "✅ '{topic}' mavzusiga {count} ta so‘z qo‘shildi!",
        'update_no_words': "❌ Yaroqli so‘zlar topilmadi.",
    
        'add_new_word': "Yangi so‘z qo‘shish",
        'edit_exist': "Mavjudini tahrirlash",
        'delete_top': "Mavzuni o‘chirish",
    
        'already_exist': "'{topic}' mavzusi allaqachon mavjud. Nima qilamiz? 👇",
        'expired_ses': "Sessiya tugadi. /update ni qayta ishga tushiring.",
    
        'edit_number': "Tahrirlash uchun so‘z raqamini kiriting.",
        'topic_del': "'{topic}' mavzusi o‘chirildi.",
        'updated_word': "Yangilandi: {eng} → {new_kor}",
    
        'nkorean_translation': "Joriy: {eng} → {current_kor}\n\nYangi koreyscha tarjimani kiriting:",
        'num_error': "Noto‘g‘ri raqam. Qayta urinib ko‘ring yoki /stop yozing.",
        'empty_topic': "Bu mavzuda hali so‘zlar yo‘q.",
    
        'study_topic': "🎯 Mavzuni tanlang:"
    }


}

def t(key, lang='en', **kwargs):
    text = TRANSLATIONS.get(lang, TRANSLATIONS['en']).get(key, key)
    if isinstance(text, list):
        return random.choice(text)
    return text.format(**kwargs)

def get_lang(context):
    return context.user_data.get('lang', 'en')

# ======================================================
# 3. DATA (numbers, alphabet)
# ======================================================

sino_korean = {
    1: "일 (il)", 2: "이 (i)", 3: "삼 (sam)", 4: "사 (sa)", 5: "오 (o')",
    6: "육 (yuk)", 7: "칠 (chil)", 8: "팔 (pal)", 9: "구 (ku)", 10: "십(shib)",
    100: "백 (pek)", 1000: "천 (chon)", 10000: "만 (man)"
}

native_korean = {
    1: "하나 (hana)", 2: "둘 (dul)", 3: "셋 (set)", 4: "넷 (net)", 5: "다섯 (dasot)",
    6: "여섯 (yosot)", 7: "일곱 (ilgop)", 8: "여덟 (yodol)", 9: "아홉 (ahop)", 10: "열 (yol)"
}

korean_letter = {
    'ㄱ': 'g/k', 'ㄴ': 'n', 'ㄷ': 'd/t', 'ㄹ': 'r/l', 'ㅁ': 'm', 'ㅂ': 'b/p', 'ㅅ': 's', 'ㅇ': 'ng/silent', 'ㅈ': 'j/ch', 'ㅊ': 'ch', 'ㅋ': 'k', 'ㅌ': 't', 'ㅍ': 'p', 'ㅎ': 'h',
    'ㅏ': 'a', 'ㅐ': 'ae', 'ㅑ': 'ya', 'ㅒ': 'yae', 'ㅓ': 'eo', 'ㅔ': 'e', 'ㅕ': 'yeo', 'ㅖ': 'ye', 'ㅗ': 'o', 'ㅘ': 'wa', 'ㅙ': 'wae', 'ㅚ': 'oe', 'ㅛ': 'yo', 'ㅜ': 'u', 'ㅝ': 'wo', 'ㅞ': 'we', 'ㅟ': 'wi', 'ㅠ': 'yu', 'ㅡ': 'eu', 'ㅢ': 'ui', 'ㅣ': 'i'
}

# ======================================================
# 4. KOREAN CONVERTER
# ======================================================

def num_to_korean(n: int) -> str:
    if n == 0: return "영"
    units = ["", "만", "억", "조"]
    small_units = ["", "십", "백", "천"]
    digits = ["", "일", "이", "삼", "사", "오", "육", "칠", "팔", "구"]
    
    if n < 10000:
        s = ""
        n_str = str(n).zfill(4)
        for i, d in enumerate(n_str):
            d = int(d)
            if d > 0:
                # Skip "일" before 십, 백, 천
                if d == 1 and (3-i) > 0:
                    s += small_units[3-i]
                else:
                    s += digits[d] + small_units[3-i]
        return s or "영"
    
    # Large numbers (same logic)
    parts = []
    unit_idx = 0
    while n > 0:
        chunk = n % 10000
        if chunk:
            chunk_str = ""
            c_str = str(chunk).zfill(4)
            for i, d in enumerate(c_str):
                d = int(d)
                if d > 0:
                    if d == 1 and (3-i) > 0:
                        chunk_str += small_units[3-i]
                    else:
                        chunk_str += digits[d] + small_units[3-i]
            parts.append(chunk_str + units[unit_idx])
        n //= 10000
        unit_idx += 1
    return "".join(reversed(parts)) or "영"

# ======================================================
# 5. UPDATE COMMAND
# ======================================================

async def update_vocab(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = get_lang(context)
    await update.message.reply_text(t('update_intro', lang))
    return UPDATE_TOPIC

async def receive_topic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    topic = update.message.text.strip()
    context.user_data['new_topic'] = topic
    lang = get_lang(context)

    if topic in KOREAN_VOCAB and KOREAN_VOCAB[topic]:
        # Topic exists → offer actions
        buttons = [
            [InlineKeyboardButton(t('add_new_word', lang), callback_data='add_words')],
            [InlineKeyboardButton(t('edit_exist', lang), callback_data='edit_words')],
            [InlineKeyboardButton(t('delete_top', lang), callback_data='delete_topic')]
        ]
        await update.message.reply_text(t('already_exist', lang, topic=topic), reply_markup=InlineKeyboardMarkup(buttons))
        return UPDATE_ACTION
    else:
        # New topic → directly ask for words
        await update.message.reply_text(t('update_words', lang))
        return UPDATE_WORDS

async def handle_topic_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    action = query.data
    topic = context.user_data.get('new_topic')

    if 'new_topic' not in context.user_data:
        await query.message.reply_text(t('expired_ses', get_lang(context)))
        return ConversationHandler.END


    if action == 'add_words':
        await query.message.reply_text(t('update_words', get_lang(context)))
        return UPDATE_WORDS

    elif action == 'edit_words':
        context.user_data['edit_topic'] = topic
        context.user_data['edit_mode'] = True
        await list_words(query, context, topic)
        await query.message.reply_text(t('edit_number', get_lang(context)))
        return UPDATE_WORDS

    elif action == 'delete_topic':
        if topic in KOREAN_VOCAB:
            del KOREAN_VOCAB[topic]
            del KOREAN_VOCAB_REVERSE[topic]
            save_vocab(KOREAN_VOCAB)
            rebuild_reverse()

            await query.message.reply_text(t('topic_del', get_lang(context)))
        context.user_data.clear()
        return ConversationHandler.END

async def receive_words(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = get_lang(context)
    topic = context.user_data.get('new_topic', 'General')
    edit_mode = context.user_data.get('edit_mode', False)

    if edit_mode:
        edit_step = context.user_data.get('edit_step')

        if edit_step == 'new_kor':
            # User sent new Korean translation
            eng = context.user_data.get('editing_eng')
            if not eng:
                await update.message.reply_text(t('expired_ses', lang))
                context.user_data.clear()
                return ConversationHandler.END

            new_kor = update.message.text.strip()
            KOREAN_VOCAB[topic][eng] = new_kor
            save_vocab(KOREAN_VOCAB)
            rebuild_reverse()

            await update.message.reply_text(t('updated_word', lang))
            context.user_data.clear()
            return ConversationHandler.END

        else:
            # First step: user sent number to edit
            try:
                num = int(update.message.text.strip())
                eng = context.user_data['numbered_words'][num]
                context.user_data['editing_eng'] = eng
                context.user_data['edit_step'] = 'new_kor'

                current_kor = KOREAN_VOCAB[topic][eng]
                await update.message.reply_text(t('nkorean_translation', lang))
            except (KeyError, ValueError):
                await update.message.reply_text(t('num_error', lang))
            return UPDATE_WORDS

    # ADD MODE
    lines = update.message.text.strip().split('\n')
    added = 0

    KOREAN_VOCAB.setdefault(topic, {})

    for line in lines:
        if '=' in line:
            eng, kor = [p.strip() for p in line.split('=', 1)]
            if eng and kor:
                KOREAN_VOCAB[topic][eng.lower()] = kor
                added += 1

    if added:
        save_vocab(KOREAN_VOCAB)
        rebuild_reverse()
        await update.message.reply_text(t('update_success', lang, count=added, topic=topic))
    else:
        await update.message.reply_text(t('update_no_words', lang))

    context.user_data.clear()
    return ConversationHandler.END

async def list_words(update: Update, context: ContextTypes.DEFAULT_TYPE, topic: str):
    words = KOREAN_VOCAB.get(topic, {})
    if not words:
        await update.message.reply_text(t('empty_topic', get_lang(context)))
        return

    text = f"**{topic}**\n\n"
    numbered = {}
    i = 1
    for eng, kor in words.items():
        text += f"{i}. {eng} → {kor}\n"
        numbered[i] = eng
        i += 1

    await update.message.reply_text(text)
    context.user_data['numbered_words'] = numbered
    context.user_data['edit_topic'] = topic
    context.user_data['current_topic'] = topic
# ======================================================
# 6. COMMANDS
# ======================================================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton(t('lang_en', 'en'), callback_data='lang_en')],
        [InlineKeyboardButton(t('lang_ru', 'en'), callback_data='lang_ru')],
        [InlineKeyboardButton(t('lang_ko', 'en'), callback_data='lang_ko')],
        [InlineKeyboardButton(t('lang_uz', 'en'), callback_data='lang_uz')]
    ]
    await update.message.reply_text(
        t('choose_lang', 'en'),
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return ASK_LANG

async def choose_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = query.data.split('_')[1]
    context.user_data['lang'] = lang
    await query.edit_message_text(
        t('welcome', lang, name=update.effective_user.first_name),
        parse_mode="Markdown"
    )
    return MAIN

async def lang_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = get_lang(context)
    keyboard = [
        [InlineKeyboardButton(t('lang_en', lang), callback_data='lang_en')],
        [InlineKeyboardButton(t('lang_ru', lang), callback_data='lang_ru')],
        [InlineKeyboardButton(t('lang_ko', lang), callback_data='lang_ko')],
        [InlineKeyboardButton(t('lang_uz', lang), callback_data='lang_uz')],
    ]
    await update.message.reply_text(t('choose_lang', lang), reply_markup=InlineKeyboardMarkup(keyboard))
    return ASK_LANG

async def score(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = get_lang(context)
    correct = context.user_data.get("correct", 0)
    wrong = context.user_data.get("wrong", 0)
    total = correct + wrong
    accuracy = (correct / total * 100) if total > 0 else 0
    streak = context.user_data.get("streak", 0)
    msg = t('score_title', lang) + t('score_correct', lang, correct=correct) + t('score_wrong', lang, wrong=wrong) + t('score_streak', lang, streak=streak) + t('score_accuracy', lang, acc=accuracy)
    await update.message.reply_text(msg, parse_mode="Markdown")

async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["active"] = False
    context.user_data.pop("quiz_format", None)
    await update.message.reply_text(t('stop', get_lang(context)))
    
async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = get_lang(context)
    await update.message.reply_text(t('help', lang), parse_mode="Markdown")
# ======================================================
# 7. STUDY & PLAY
# ======================================================

async def study(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = get_lang(context)
    buttons = [
        [InlineKeyboardButton(t('korean_alp', lang), callback_data='study_alphabet')],
        [InlineKeyboardButton(t('korean_num', lang), callback_data='study_numbers')],
        [InlineKeyboardButton(t('korean_word', lang), callback_data='study_words')]
    ]
    await update.message.reply_text(t('study_choose_mode', lang), reply_markup=InlineKeyboardMarkup(buttons))

async def play(update, context):
    keyboard = [
        [InlineKeyboardButton("✍ Text Answer", callback_data="quiz_format_text")],
        [InlineKeyboardButton("🧪 Test (MCQ)", callback_data="quiz_format_mcq")]
    ]

    await update.message.reply_text(
        "Choose quiz format:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    return MAIN   

# ======================================================
# 8. BUTTON HANDLER
# ======================================================

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.message.delete()
    data = query.data
    lang = get_lang(context)

    # Study modes
    if data == 'study_words':
        topics = list(KOREAN_VOCAB.keys())
        buttons = []

        for i in range(0, len(topics), 2):
            row = [
                InlineKeyboardButton(topics[i], callback_data=f'study_topic_{topics[i]}')
            ]
            if i + 1 < len(topics):
                row.append(
                    InlineKeyboardButton(topics[i + 1], callback_data=f'study_topic_{topics[i + 1]}')
                )
            buttons.append(row)

        await query.message.reply_text(
            t('study_topic', get_lang(context)),
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        return


    if data.startswith('study_topic_'):
        topic = data[len('study_topic_'):]
        words = KOREAN_VOCAB.get(topic, {})
    
        if not words:
            await query.message.reply_text(t('empty_topic', get_lang(context)))
            return
    
        text = f"**{topic}**\n\n"
        for eng, kor in words.items():
            text += f"• {eng} → {kor}\n"
    
        await query.message.reply_text(text, parse_mode="Markdown")
        return

    # STUDY MODES
    if data == 'study_alphabet':
        text = t('study_alphabet', lang) + "\n"
        for k, v in korean_letter.items():
            text += f"{k} → {v}\n"
        await query.message.reply_text(text, parse_mode="Markdown")
        return

    elif data == 'study_numbers':
        text = t('study_sino', lang) + "\n"
        for k, v in sino_korean.items():
            text += f"{k} → {v}\n"
        text += "\n" + t('study_native', lang) + "\n"
        for k, v in native_korean.items():
            text += f"{k} → {v}\n"
        await query.message.reply_text(text, parse_mode="Markdown")
        await query.message.reply_text(t('study_ready', lang))
        return

    elif data == 'study_words':
        text = t('study_words', lang)
        for eng, kor in KOREAN_VOCAB.items():
            text += f"{eng} → {kor}\n"
        await query.message.reply_text(text, parse_mode="Markdown")
        return

    # Word quiz: choose topic
    if data == 'play_words':
        topics = list(KOREAN_VOCAB.keys())
        buttons = []

        for i in range(0, len(topics), 2):
            row = [
                InlineKeyboardButton(topics[i], callback_data=f'topic_{topics[i]}')
            ]
            if i + 1 < len(topics):
                row.append(
                    InlineKeyboardButton(topics[i + 1], callback_data=f'topic_{topics[i + 1]}')
                )
            buttons.append(row)

        await query.message.reply_text(t('study_topic', lang),reply_markup=InlineKeyboardMarkup(buttons))
        return
    

    # Topic chosen → direction
    if data.startswith('topic_'):
        topic = data[6:]
        context.user_data['current_topic'] = topic
        buttons = [
            [InlineKeyboardButton(t('eng_to_kore', lang), callback_data='dir_eng2kor')],
            [InlineKeyboardButton(t('kore_to_eng', lang), callback_data='dir_kor2eng')]
        ]
        await query.message.reply_text(t('play_choose_mode', get_lang(context)), reply_markup=InlineKeyboardMarkup(buttons))
        return

    # Direction chosen → start vocab quiz
    if data in ('dir_eng2kor', 'dir_kor2eng'):
        context.user_data['quiz_type'] = 'vocab'
        context.user_data['direction'] = data
        context.user_data['active'] = True
        context.user_data["correct"] = 0
        context.user_data["wrong"] = 0
        await send_new_question(update, context)
        return

    if data == 'play_numbers':
        buttons = [
            [InlineKeyboardButton(t('mode_num_to_target', lang), callback_data='num2kor')],
            [InlineKeyboardButton(t('mode_target_to_num', lang), callback_data='kor2num')]
        ]
        await query.message.reply_text(t('play_choose_mode', get_lang(context)), reply_markup=InlineKeyboardMarkup(buttons))
        return

    if data in ('num2kor', 'kor2num'):
        context.user_data['quiz_type'] = 'number'
        context.user_data['direction'] = data
        buttons = [
            [InlineKeyboardButton(t('level_easy', lang), callback_data='level_easy')],
            [InlineKeyboardButton(t('level_medium', lang), callback_data='level_medium')],
            [InlineKeyboardButton(t('level_hard', lang), callback_data='level_hard')]
        ]
        await query.message.reply_text(t('choose_level', lang), reply_markup=InlineKeyboardMarkup(buttons))
        return

    # DIFFICULTY (only for numbers)
    if data.startswith('level_'):
        if context.user_data.get('quiz_type') == 'number':
            level_key = data.split('_')[1]
            context.user_data["level"] = level_key
            context.user_data["active"] = True

            # Human-readable level text
            level_text = {
                "easy": t('level_easy', lang),
                "medium": t('level_medium', lang),
                "hard": t('level_hard', lang)
            }[level_key]

            await query.message.reply_text(
                t(
                    'game_start',
                    lang,
                    level=level_text,
                ),
                parse_mode="Markdown"
            )

        await send_new_question(update, context)
    return

async def handle_mcq_answer(update, context):
    query = update.callback_query
    lang = get_lang
    await query.answer()

    selected = int(query.data.split("_")[1])
    correct = context.user_data.get("mcq_correct")

    if selected == correct:
        context.user_data["correct"] = context.user_data.get("correct", 0) + 1
        result = t('correct', lang)
    else:
        context.user_data["wrong"] = context.user_data.get("wrong", 0) + 1
        result = t('wrong', lang)

    await query.edit_message_text(result)
    await send_new_question(update, context)

# ======================================================
# 9. QUESTION
# ======================================================

async def send_new_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("active"):
        return

    lang = get_lang(context)
    quiz_type = context.user_data.get('quiz_type')

    if quiz_type == 'vocab':
        topic = context.user_data.get('current_topic')
        words = KOREAN_VOCAB.get(topic, {})
        direction = context.user_data['direction']

        quiz_format = context.user_data.get("quiz_format", "text")

        if quiz_format == "mcq":
            await send_mcq_question(update, context, words, direction)
            return

        # TEXT MODE (original behavior)
        if direction == 'dir_eng2kor':
            eng = random.choice(list(words.keys()))
            expected = words[eng]
            question = t('question_eng_to_kor', lang, eng=eng, parse_mode="Markdown")
        else:
            kor = random.choice(list(words.values()))
            expected = KOREAN_VOCAB_REVERSE.get(topic, {}).get(kor.lower())
            if not expected:
                return
            question = t('question_kor_to_eng', lang, kor=kor, parse_mode="Markdown")

        context.user_data["answer_expected"] = expected.lower()
        context.user_data["answer_type"] = "word"

        await update.effective_chat.send_message(question)
        return
    else:
        level = context.user_data.get("level", "easy")
        if level == "easy":
            num = random.randint(1, 10)
        elif level == "medium":
            num = random.randint(1, 1000)
        else:
            num = random.randint(1, 999999)
            
        kor = num_to_korean(num)
        direction = context.user_data['direction']

        if direction == 'num2kor':
            question = t('question_num_to_target', lang, num=num, parse_mode="Markdown")
            expected = kor.lower()
            expected_type = "word"
        else:
            question = t('question_target_to_num', lang, word=kor, parse_mode="Markdown")
            expected = str(num)
            expected_type = "num"

        # Set number quiz state
        context.user_data["vocab_active"] = False
        context.user_data["answer_expected"] = expected.lower()
        context.user_data["answer_type"] = "word"

    # Set common state
    context.user_data["answer_expected"] = expected
    context.user_data["answer_type"] = expected_type if quiz_type == 'number' else "word"

    await update.effective_chat.send_message(question)

async def send_mcq_question(update, context, words, direction):

    lang = get_lang(context)
    if len(words) < 3:
        await update.effective_message.reply_text("Not enough words for test mode.")
        return

    eng = random.choice(list(words.keys()))
    kor = words[eng]

    if direction == "dir_eng2kor":
        question_text = t('question_eng_to_kor', lang, eng=eng)
        correct = kor

        all_kor = [v for k, v in words.items() if k != eng]
        wrong = random.sample(all_kor, 2)

    else:
        question_text = t('question_kor_to_eng', lang, kor=kor)
        correct = eng

        all_eng = [k for k in words.keys() if k != eng]
        wrong = random.sample(all_eng, 2)

    options = wrong + [correct]
    random.shuffle(options)

    context.user_data["mcq_correct"] = options.index(correct)

    symbols = ["①", "②", "③"]
    keyboard = [
        [InlineKeyboardButton(f"{symbols[i]} {opt}", callback_data=f"mcq_{i}")]
        for i, opt in enumerate(options)
    ]

    score_text = f"\n\nScore: {context.user_data.get('correct',0)}✅ {context.user_data.get('wrong',0)}❌"

    await update.effective_message.reply_text(
        question_text + "\n\n" +
        "\n".join([f"{symbols[i]} {opt}" for i, opt in enumerate(options)]) +
        score_text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ======================================================
# 10. CHECK ANSWER
# ======================================================

async def check_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("active"):
        return

    lang = get_lang(context)
    user_input = update.message.text.strip().lower()
    expected = context.user_data.get("answer_expected")
    expected_type = context.user_data.get("answer_type", "word")

    # VOCABULARY QUIZ
    if context.user_data.get("quiz_type") == "vocab":
        ok = user_input == expected.lower()

        if ok:
            context.user_data["correct"] = context.user_data.get("correct", 0) + 1
            await update.message.reply_text(t('positive', lang))
        else:
            context.user_data["wrong"] = context.user_data.get("wrong", 0) + 1
            await update.message.reply_text(
                f"{t('negative', lang)}\n"
                f"{t('correct_answer', lang, answer=expected.title())}"
            )
    else:
        # NUMBER QUIZ
        ok = False
        if expected_type == "word":
            norm_user = "".join(c for c in user_input if c.isalnum()).lower()
            norm_exp = "".join(c for c in str(expected) if c.isalnum()).lower()
            ok = norm_user == norm_exp
        else:
            try:
                cleaned = user_input.replace(",", "").replace(" ", "").replace(".", "")
                ok = str(int(cleaned)) == expected
            except:
                ok = False

        if ok:
            context.user_data["correct"] = context.user_data.get("correct", 0) + 1
            context.user_data["streak"] = context.user_data.get("streak", 0) + 1
            context.user_data["wrong_streak"] = 0
            await update.message.reply_text(t('positive', lang))

            if context.user_data["streak"] >= 5:
                old = context.user_data.get("level", "easy")
                if old == "easy":
                    context.user_data["level"] = "medium"
                    await update.message.reply_text(t('level_up_easy', lang))
                elif old == "medium":
                    context.user_data["level"] = "hard"
                    await update.message.reply_text(t('level_up_medium', lang))
                context.user_data["streak"] = 0
        else:
            context.user_data["wrong"] = context.user_data.get("wrong", 0) + 1
            context.user_data["wrong_streak"] = context.user_data.get("wrong_streak", 0) + 1
            context.user_data["streak"] = 0

            show = expected
            if expected_type == "num":
                word = num_to_korean(int(expected))
                show = f"{expected} ({word})"

            await update.message.reply_text(
                f"{t('negative', lang)}\n"
                f"{t('correct_answer', lang, answer=show)}"
            )

            if context.user_data["wrong_streak"] >= 3:
                await update.message.reply_text(t('tip', lang))
                context.user_data["wrong_streak"] = 0

    # Continue quiz
    await send_new_question(update, context)

async def select_quiz_format(update, context):
    query = update.callback_query
    await query.answer()

    format_selected = query.data.split("_")[-1]
    context.user_data["quiz_format"] = format_selected

    # Show word quiz menu (like play_words)
    buttons = [
        [InlineKeyboardButton("📘 Words", callback_data="play_words")],
        [InlineKeyboardButton("🔢 Numbers", callback_data="play_numbers")]
    ]

    await query.edit_message_text(
        "Choose quiz type:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

# ======================================================
# 10. CONVERSATION HANDLER
# ======================================================

conv_handler = ConversationHandler(
    entry_points=[
        CommandHandler('start', start),
        CommandHandler('lang', lang_command),
        CommandHandler('update', update_vocab),
    ],
    states={
        ASK_LANG: [CallbackQueryHandler(choose_language, pattern='^lang_')],
        UPDATE_TOPIC: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_topic)],
        UPDATE_ACTION: [CallbackQueryHandler(handle_topic_action, pattern='^(add_words|edit_words|delete_topic)$')],
        UPDATE_WORDS: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_words)],
    },
    fallbacks=[
        CommandHandler("stop", stop)
    ],
)

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(conv_handler)

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("stop", stop))
app.add_handler(CommandHandler("study", study))
app.add_handler(CommandHandler("practice", play))
app.add_handler(CommandHandler("score", score))
app.add_handler(CommandHandler("lang", lang_command))
app.add_handler(CommandHandler("update", update_vocab))
app.add_handler(CommandHandler("help", help_cmd))
app.add_handler(CallbackQueryHandler(handle_mcq_answer, pattern="^mcq_"))
app.add_handler(CallbackQueryHandler(select_quiz_format, pattern="^quiz_format_"))
app.add_handler(CallbackQueryHandler(button_handler, pattern="^(?!add_words|edit_words|delete_topic).*"))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, check_answer))

print("Bot started!")
app.run_polling()