import spacy
import textdescriptives as td

nlp = spacy.load("fr_dep_news_trf")
nlp.add_pipe('textdescriptives')
doc = nlp("c'est intéressant")
spacy.displacy.serve(doc, style="dep")

doc = nlp("c'est une campagne de pub ciblant les enfants")
spacy.displacy.serve(doc, style="dep")

doc = nlp("ça fait sens avec ce qu'on a vu précédemment")
spacy.displacy.serve(doc, style="dep")

doc = nlp("je sais pas elle semblait contrariée cette framboise")
spacy.displacy.serve(doc, style="dep")