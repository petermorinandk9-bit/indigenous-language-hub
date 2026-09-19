import csv

def generate_large_corpus():
    entries = [
        # Core & Environment
        ("Lakȟóta", "n", "Lakota person, ally; speak Lakota", "Core vocabulary baseline"),
        ("iyápi", "n", "language, speech, word", "Core vocabulary baseline"),
        ("pté", "n", "buffalo", "Core vocabulary baseline"),
        ("waȟpé", "n", "leaf", "Core vocabulary baseline"),
        ("mni", "n", "water", "Core vocabulary baseline"),
        ("čhaŋ", "n", "wood, tree", "Core vocabulary baseline"),
        ("čhaŋcéǧa", "n", "drum", "Core vocabulary baseline"),
        ("čhaŋté", "n", "heart", "Core vocabulary baseline"),
        ("pahá", "n", "hill, mountain", "Core vocabulary baseline"),
        ("makȟóčhe", "n", "land, country, earth", "Core vocabulary baseline"),
        ("wičháša", "n", "man", "Core vocabulary baseline"),
        ("wiyáŋ", "n", "woman", "Core vocabulary baseline"),
        ("tȟoká", "n", "enemy, stranger", "Core vocabulary baseline"),
        ("waŋyáŋka", "v", "to see, to look at", "Core vocabulary baseline"),
        ("slolyé", "v", "to know, to understand", "Core vocabulary baseline"),
        
        # Family & People
        ("até", "n", "father", "Family vocabulary"),
        ("iná", "n", "mother", "Family vocabulary"),
        ("takóža", "n", "grandchild", "Family vocabulary"),
        ("tȟuŋwáŋ", "n", "grandfather", "Family vocabulary"),
        ("hokšíla", "n", "boy", "Everyday vocabulary"),
        ("wičhíŋčana", "n", "girl", "Everyday vocabulary"),
        ("hųká", "n", "ancestor, chief, elder, relative", "Cultural vocabulary"),
        
        # Anatomy & Nature
        ("wahí", "n", "tooth, bone", "Anatomy vocabulary"),
        ("pȟtéte", "n", "rib", "Anatomy vocabulary"),
        ("pȟá", "n", "head", "Anatomy vocabulary"),
        ("ištá", "n", "eye", "Anatomy vocabulary"),
        ("ho", "n", "voice, neck", "Anatomy vocabulary"),
        ("pȟeží", "n", "grass, hay", "Flora vocabulary"),
        ("čhaxóta", "n", "ashes", "Flora/Material"),
        ("pséxte", "n", "ash tree (Fraxinus)", "Flora vocabulary"),
        ("thathóka", "n", "antelope", "Fauna"),
        ("tatáka", "n", "bull, buffalo bull", "Fauna"),
        ("šúŋka", "n", "dog", "Fauna"),
        ("maǧá", "n", "goose", "Fauna"),
        ("čhápa", "n", "beaver", "Fauna"),
        ("xoká", "n", "badger", "Fauna"),
        ("Wakíŋyaŋ", "n", "thunder", "Nature"),
        
        # Numbers
        ("waŋží", "num", "one", "Numbers baseline"),
        ("núŋpa", "num", "two", "Numbers baseline"),
        ("yámni", "num", "three", "Numbers baseline"),
        ("tópa", "num", "four", "Numbers baseline"),
        ("záptaŋ", "num", "five", "Numbers baseline"),
        ("šákpe", "num", "six", "Numbers baseline"),
        ("šákowiŋ", "num", "seven", "Numbers baseline"),
        ("šápȟe", "num", "eight", "Numbers baseline"),
        ("napčéwaŋža", "num", "ten", "Numbers baseline"),
        
        # Verbs & Actions
        ("yaté", "v", "to eat", "Action baseline"),
        ("mná", "v", "to gather, to collect", "Action baseline"),
        ("hiyo", "v", "go or come to fetch", "Action baseline"),
        ("kiktá", "v", "arise, get up", "Action baseline"),
        ("iyų́ɣa", "v", "to ask", "Action baseline"),
        ("hí", "v", "to arrive here, to come", "Action baseline"),
        ("gli", "v", "to arrive home, to return here", "Action baseline"),
        ("inážiŋ", "v", "to stand up, to halt", "Action baseline"),
        ("yúha", "v", "to have, to hold, to possess", "Action baseline"),
        ("tmá", "v", "to cut with a knife, to carve", "Action baseline"),
        ("kaksá", "v", "to chop off, to sever", "Action baseline"),
        ("kapá", "v", "to surpass, to excel", "Action baseline"),
        ("yawá", "v", "to read, to count", "Action baseline"),
        ("čhíŋ", "v", "to want, to desire", "Action baseline"),
        
        # Descriptives & Culture
        ("wašté", "adj", "good, beautiful, nice", "Descriptive baseline"),
        ("súta", "adj", "hard, strong, firm", "Descriptive baseline"),
        ("tȟaŋka", "adj", "big, large, great", "Descriptive baseline"),
        ("šíča", "adj", "bad", "Descriptive baseline"),
        ("wakȟáŋ", "adj", "sacred, holy, mysterious", "Cultural vocabulary"),
        ("wičhóhą", "n", "custom, behavior, way of life", "Cultural vocabulary"),
        ("wičhóiyake", "n", "story, history, account", "Cultural vocabulary"),
        ("wówašte", "n", "goodness, grace, blessing", "Cultural vocabulary"),
        ("wakȟályapi", "n", "soup, broth", "Food baseline"),
        ("wagmíza", "n", "pumpkin, squash", "Food baseline"),
        ("Wóuŋspe", "n", "lesson, learning", "Education"),
        ("Wówapi", "n", "book, paper, letter", "Education"),
        ("Aŋpétu", "n", "day", "Time baseline"),
        ("Haŋhépi", "n", "night", "Time baseline")
    ]
    
    filename = "lakota_words.csv"
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["lakota_word", "word_class", "english_translation", "audio_url", "source_notes"])
        for word, w_class, trans, notes in entries:
            writer.writerow([word, w_class, trans, "", notes])
            
    print(f"[SUCCESS] Generated {len(entries)} records into '{filename}' readiness for database import.")

if __name__ == "__main__":
    generate_large_corpus()