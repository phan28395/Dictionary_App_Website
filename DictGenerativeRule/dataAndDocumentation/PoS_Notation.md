    """Enumeration of single-letter POS codes with their meanings."""
    https://ucrel.lancs.ac.uk/claws7tags.html
    ARTICLE = 'a'          # AT, AT1 in CLAWS7 (In Data)
    VERB = 'v'             # VB*, VD*, VH*, VM, VV* in CLAWS7 (In Data) 
    Adjective = "j"        # JJ, JJR, JJT, JK (In Data)
    CONJUNCTION = 'c'      # CC, CCB, CS* in CLAWS7 (In Data)
    PREPOSITION = 'i'      # IF, II, IO, IW in CLAWS7 (In Data)
    LETTER = 'l'           # Not in CLAWS7, custom addition (Not in Data)
    PRONOUN = 'p'          # PN*, PP* in CLAWS7 (In Data)
    DETERMINER = 'd'       # DA*, DB*, DD* in CLAWS7 (In Data)
    NEGATION = 'x'         # XX in CLAWS7 (Not in Data)
    ADVERB = 'r'           # RA, RG*, RL, RP, RR*, RT in CLAWS7 (in Data)
    NOUN = 'n'             # NN*, NP* in CLAWS7 (in Data)
    NUMERAL = 'm'          # MC*, MD, MF in CLAWS7 (Not in Data)
    INTERJECTION = 'u'     # UH in CLAWS7 (Not in Data)
    INFINITIVE MARKER = "t"  # Only one word "to"

    Tab: 1 lemmas
    Column B: "lemma"
    Column C: "PoS
    
    To-Do:
    ARTICLE = 'a' (Skip for now, only "the", "a" and "an")
    CONJUNCTION = 'c'(Done)
    PREPOSITION = 'i'  (done)
    PRONOUN = 'p' (done)
    DETERMINER = 'd' (done)
    ADVERB = 'r'  
    INFINITIVE MARKER = "t"