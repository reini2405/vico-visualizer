import random
import argparse

# Kategorien mit Tags
tags = {
    "Mood": [
        "🌌 dreamstate", "🌪 trance pulse", "🕯 ritual flow", "💤 velvet calm",
        "🌘 nocturnal shimmer", "✨ ambient bloom", "🕊 breath of dusk"
    ],
    "FX / Sound": [
        "🔮 shimmer delay", "🌬 breath fx", "📡 stereo fog", "🫧 reverb silk",
        "🧼 washed echoes", "🌊 emotional glide", "⛓ glitch veil"
    ],
    "Culture / Style": [
        "🕌 arabic spirit", "🪬 persian bloom", "🎎 silk fusion", "🪘 tribal soul",
        "🐫 desert soul", "🧿 middle eastern echo", "🪕 maqam whisper"
    ],
    "Voice / Expression": [
        "💋 seductive aaaaah", "👁 mystical vowels", "🔊 vowel chant",
        "🧘‍♀️ breath meditation", "🕷 whispered tones", "🫁 sigh and shimmer"
    ],
    "Emotion / Aura": [
        "💔 longing echo", "🕸 fragile beauty", "💄 dark allure", "🫀 deep yearning",
        "🔥 slow burn", "✨ sensual shimmer", "🌫 faded memory"
    ]
}

def generate_tags(num_categories=3, tags_per_category=2):
    selected_tags = []
    chosen_cats = random.sample(list(tags.keys()), num_categories)
    for cat in chosen_cats:
        selected = random.sample(tags[cat], tags_per_category)
        selected_tags.extend(selected)
    return "[tags]\n" + "\n".join(selected_tags) + "\n[/tags]"

def print_all_tags():
    output = ["[tags]"]
    for category, tag_list in tags.items():
        output.append(f"# {category}")
        output.extend(tag_list)
    output.append("[/tags]")
    return "\n".join(output)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--all", action="store_true", help="Alle Kategorien und Tags anzeigen")
    args = parser.parse_args()

    if args.all:
        print(print_all_tags())
    else:
        print(generate_tags())

