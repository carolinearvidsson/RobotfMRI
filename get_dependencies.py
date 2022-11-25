import spacy
import textdescriptives as td

nlp = spacy.load("fr_dep_news_trf")
nlp.add_pipe('textdescriptives')
for token in doc:
    print(token._.dependency_distance)
spacy.displacy.serve(doc, style="dep")

doc = nlp("ouais c'est vrai que le fait d'utiliser des super héros euh")
spacy.displacy.serve(doc, style="dep")

doc = nlp("ouais c'est pour faire le le thème super-héros")
spacy.displacy.serve(doc, style="dep")

doc = nlp("je sais pas elle semblait contrariée cette framboise")
spacy.displacy.serve(doc, style="dep")