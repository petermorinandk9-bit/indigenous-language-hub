import csv
from pathlib import Path

def generate_full_seed():
    entries = [
        # Core & Environment
        ("Lakȟóta", "Lakota person, ally; speak Lakota", "n", "Core Corpus", "Public Domain", "SLO", "Core vocabulary baseline"),
        ("iyápi", "language, speech, word", "n", "Core Corpus", "Public Domain", "SLO", "Core vocabulary baseline"),
        ("pté", "buffalo", "n", "Core Corpus", "Public Domain", "SLO", "Core vocabulary baseline"),
        ("waȟpé", "leaf", "n", "Core Corpus", "Public Domain", "SLO", "Core vocabulary baseline"),
        ("mni", "water", "n", "Core Corpus", "Public Domain", "SLO", "Core vocabulary baseline"),
        ("čhaŋ", "wood, tree", "n", "Core Corpus", "Public Domain", "SLO", "Core vocabulary baseline"),
        ("čhaŋcéǧa", "drum", "n", "Core Corpus", "Public Domain", "SLO", "Core vocabulary baseline"),
        ("čhaŋté", "heart", "n", "Core Corpus", "Public Domain", "SLO", "Core vocabulary baseline"),
        ("pahá", "hill, mountain", "n", "Core Corpus", "Public Domain", "SLO", "Core vocabulary baseline"),
        ("makȟóčhe", "land, country, earth", "n", "Core Corpus", "Public Domain", "SLO", "Core vocabulary baseline"),
        ("wičháša", "man", "n", "Core Corpus", "Public Domain", "SLO", "Core vocabulary baseline"),
        ("wiyáŋ", "woman", "n", "Core Corpus", "Public Domain", "SLO", "Core vocabulary baseline"),
        ("tȟoká", "enemy, stranger", "n", "Core Corpus", "Public Domain", "SLO", "Core vocabulary baseline"),
        ("waŋyáŋka", "to see, to look at", "v", "Core Corpus", "Public Domain", "SLO", "Core vocabulary baseline"),
        ("slolyé", "to know, to understand", "v", "Core Corpus", "Public Domain", "SLO", "Core vocabulary baseline"),
        
        # Family & People
        ("até", "father", "n", "Family Corpus", "Public Domain", "SLO", "Family vocabulary"),
        ("iná", "mother", "n", "Family Corpus", "Public Domain", "SLO", "Family vocabulary"),
        ("takóža", "grandchild", "n", "Family Corpus", "Public Domain", "SLO", "Family vocabulary"),
        ("tȟuŋwáŋ", "grandfather", "n", "Family Corpus", "Public Domain", "SLO", "Family vocabulary"),
        ("hokšíla", "boy", "n", "Everyday Corpus", "Public Domain", "SLO", "Everyday vocabulary"),
        ("wičhíŋčana", "girl", "n", "Everyday Corpus", "Public Domain", "SLO", "Everyday vocabulary"),
        ("hųká", "ancestor, chief, elder, relative", "n", "Cultural Corpus", "Public Domain", "SLO", "Cultural vocabulary"),
        ("kuzá", "aunt", "n", "Family Corpus", "Public Domain", "SLO", "Family vocabulary"),
        ("tȟéši", "uncle", "n", "Family Corpus", "Public Domain", "SLO", "Family vocabulary"),
        ("taŋyáŋ", "well, properly, safely", "adv", "Grammar Corpus", "Public Domain", "SLO", "Adverbial baseline"),
        ("mitáku", "my relative, my friend", "n", "Family Corpus", "Public Domain", "SLO", "Relationship baseline"),

        # Anatomy & Nature
        ("wahí", "tooth, bone", "n", "Anatomy Corpus", "Public Domain", "SLO", "Anatomy vocabulary"),
        ("pȟtéte", "rib", "n", "Anatomy Corpus", "Public Domain", "SLO", "Anatomy vocabulary"),
        ("pȟá", "head", "n", "Anatomy Corpus", "Public Domain", "SLO", "Anatomy vocabulary"),
        ("ištá", "eye", "n", "Anatomy Corpus", "Public Domain", "SLO", "Anatomy vocabulary"),
        ("ho", "voice, neck", "n", "Anatomy Corpus", "Public Domain", "SLO", "Anatomy vocabulary"),
        ("pȟeží", "grass, hay", "n", "Flora Corpus", "Public Domain", "SLO", "Flora vocabulary"),
        ("čhaxóta", "ashes", "n", "Flora/Material", "Public Domain", "SLO", "Material baseline"),
        ("pséxte", "ash tree (Fraxinus)", "n", "Flora Corpus", "Public Domain", "SLO", "Flora vocabulary"),
        ("thathóka", "antelope", "n", "Fauna Corpus", "Public Domain", "SLO", "Fauna baseline"),
        ("tatáka", "bull, buffalo bull", "n", "Fauna Corpus", "Public Domain", "SLO", "Fauna baseline"),
        ("šúŋka", "dog", "n", "Fauna Corpus", "Public Domain", "SLO", "Fauna baseline"),
        ("maǧá", "goose", "n", "Fauna Corpus", "Public Domain", "SLO", "Fauna baseline"),
        ("čhápa", "beaver", "n", "Fauna Corpus", "Public Domain", "SLO", "Fauna baseline"),
        ("xoká", "badger", "n", "Fauna Corpus", "Public Domain", "SLO", "Fauna baseline"),
        ("Wakíŋyaŋ", "thunder", "n", "Nature Corpus", "Public Domain", "SLO", "Nature baseline"),
        ("p’ó", "fog, mist", "n", "Nature Corpus", "Public Domain", "SLO", "Weather baseline"),
        ("mağáȟpiya", "cloud", "n", "Nature Corpus", "Public Domain", "SLO", "Weather baseline"),
        ("wičhàhpi", "star", "n", "Nature Corpus", "Public Domain", "SLO", "Astronomy baseline"),
        ("anpó", "dawn, morning", "n", "Time Corpus", "Public Domain", "SLO", "Time baseline"),

        # Numbers
        ("waŋží", "one", "num", "Numbers Corpus", "Public Domain", "SLO", "Numbers baseline"),
        ("núŋpa", "two", "num", "Numbers Corpus", "Public Domain", "SLO", "Numbers baseline"),
        ("yámni", "three", "num", "Numbers Corpus", "Public Domain", "SLO", "Numbers baseline"),
        ("tópa", "four", "num", "Numbers Corpus", "Public Domain", "SLO", "Numbers baseline"),
        ("záptaŋ", "five", "num", "Numbers Corpus", "Public Domain", "SLO", "Numbers baseline"),
        ("šákpe", "six", "num", "Numbers Corpus", "Public Domain", "SLO", "Numbers baseline"),
        ("šákowiŋ", "seven", "num", "Numbers Corpus", "Public Domain", "SLO", "Numbers baseline"),
        ("šápȟe", "eight", "num", "Numbers Corpus", "Public Domain", "SLO", "Numbers baseline"),
        ("kopáwiŋ", "nine", "num", "Numbers Corpus", "Public Domain", "SLO", "Numbers baseline"),
        ("napčéwaŋža", "ten", "num", "Numbers Corpus", "Public Domain", "SLO", "Numbers baseline"),
        ("akáwiŋ", "eleven", "num", "Numbers Corpus", "Public Domain", "SLO", "Numbers baseline"),

        # Verbs & Actions
        ("yaté", "to eat", "v", "Action Corpus", "Public Domain", "SLO", "Action baseline"),
        ("mná", "to gather, to collect", "v", "Action Corpus", "Public Domain", "SLO", "Action baseline"),
        ("hiyo", "go or come to fetch", "v", "Action Corpus", "Public Domain", "SLO", "Action baseline"),
        ("kiktá", "arise, get up", "v", "Action Corpus", "Public Domain", "SLO", "Action baseline"),
        ("iyų́ɣa", "to ask", "v", "Action Corpus", "Public Domain", "SLO", "Action baseline"),
        ("hí", "to arrive here, to come", "v", "Action Corpus", "Public Domain", "SLO", "Action baseline"),
        ("gli", "to arrive home, to return here", "v", "Action Corpus", "Public Domain", "SLO", "Action baseline"),
        ("inážiŋ", "to stand up, to halt", "v", "Action Corpus", "Public Domain", "SLO", "Action baseline"),
        ("yúha", "to have, to hold, to possess", "v", "Action Corpus", "Public Domain", "SLO", "Action baseline"),
        ("tmá", "to cut with a knife, to carve", "v", "Action Corpus", "Public Domain", "SLO", "Action baseline"),
        ("kaksá", "to chop off, to sever", "v", "Action Corpus", "Public Domain", "SLO", "Action baseline"),
        ("kapá", "to surpass, to excel", "v", "Action Corpus", "Public Domain", "SLO", "Action baseline"),
        ("yawá", "to read, to count", "v", "Action Corpus", "Public Domain", "SLO", "Action baseline"),
        ("čhíŋ", "to want, to desire", "v", "Action Corpus", "Public Domain", "SLO", "Action baseline"),
        ("wašté", "good, beautiful, nice", "adj", "Descriptive Corpus", "Public Domain", "SLO", "Descriptive baseline"),
        ("súta", "hard, strong, firm", "adj", "Descriptive Corpus", "Public Domain", "SLO", "Descriptive baseline"),
        ("tȟaŋka", "big, large, great", "adj", "Descriptive Corpus", "Public Domain", "SLO", "Descriptive baseline"),
        ("šíča", "bad", "adj", "Descriptive Corpus", "Public Domain", "SLO", "Descriptive baseline"),
        ("wakȟáŋ", "sacred, holy, mysterious", "adj", "Cultural Corpus", "Public Domain", "SLO", "Cultural vocabulary"),
        ("wičhóhą", "custom, behavior, way of life", "n", "Cultural Corpus", "Public Domain", "SLO", "Cultural vocabulary"),
        ("wičhóiyake", "story, history, account", "n", "Cultural Corpus", "Public Domain", "SLO", "Cultural vocabulary"),
        ("wówašte", "goodness, grace, blessing", "n", "Cultural Corpus", "Public Domain", "SLO", "Cultural vocabulary"),
        ("wakȟályapi", "soup, broth", "n", "Food Corpus", "Public Domain", "SLO", "Food baseline"),
        ("wagmíza", "pumpkin, squash", "n", "Food Corpus", "Public Domain", "SLO", "Food baseline"),
        ("Wóuŋspe", "lesson, learning", "n", "Education Corpus", "Public Domain", "SLO", "Education"),
        ("Wówapi", "book, paper, letter", "n", "Education Corpus", "Public Domain", "SLO", "Education"),
        ("Aŋpétu", "day", "n", "Time Corpus", "Public Domain", "SLO", "Time baseline"),
        ("Haŋhépi", "night", "n", "Time Corpus", "Public Domain", "SLO", "Time baseline"),
        
        # Additional Expanded Verbs & Common Phrases
        ("yuhá", "to have, own", "v", "Action Corpus", "Public Domain", "SLO", "Expanded vocabulary"),
        ("waŋí", "to see", "v", "Action Corpus", "Public Domain", "SLO", "Expanded vocabulary"),
        ("lowáŋ", "to sing", "v", "Action Corpus", "Public Domain", "SLO", "Expanded vocabulary"),
        ("pahí", "to gather together", "v", "Action Corpus", "Public Domain", "SLO", "Expanded vocabulary"),
        ("gliha", "to return walking", "v", "Action Corpus", "Public Domain", "SLO", "Expanded vocabulary"),
        ("wačhí", "to dance", "v", "Action Corpus", "Public Domain", "SLO", "Expanded vocabulary"),
        ("khúta", "low, downward", "adv", "Grammar Corpus", "Public Domain", "SLO", "Expanded vocabulary"),
        ("iyówaŋǧe", "more, additionally", "adv", "Grammar Corpus", "Public Domain", "SLO", "Expanded vocabulary"),
        ("tȟápa", "ball, football", "n", "Material Corpus", "Public Domain", "SLO", "Expanded vocabulary"),
        ("pahú", "hill summit, nose of hill", "n", "Geography Corpus", "Public Domain", "SLO", "Expanded vocabulary")
    ]
    
    csv_path = Path("lakota_seed.csv")
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["lakota_word", "english_translation", "word_class", "source", "license", "orthography", "notes", "audio_url"])
        for item in entries:
            writer.writerow([item[0], item[1], item[2], item[3], item[4], item[5], item[6], ""])
            
    print(f"[SUCCESS] Written {len(entries)} records to 'lakota_seed.csv'.")

if __name__ == "__main__":
    generate_full_seed()