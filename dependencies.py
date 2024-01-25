import spacy
import textdescriptives as td

nlp = spacy.load("fr_dep_news_trf")
nlp.add_pipe('textdescriptives/dependency_distance')

class Dependencies:

    def get_tdl(self, utterance): # Utterance is a string where tokens are surrounded by black spaces
        unwanted = ['ah', 'euh', '***', 'ouais', 'oui', 'ok', 'non', 'voilà', '******', '*']
        print(utterance) # oui och non är på gränsen om de ska tas bort eller ej
        for value in unwanted:
            if value in utterance.split():
                utterance = utterance.split()
                utterance.remove(value)
                utterance = ' '.join(utterance)

        doc = nlp(utterance)
        #spacy.displacy.serve(doc, style="dep")

        tdl = 0
        for token in doc:
            tdl += token._.dependency_distance['dependency_distance']
        return tdl

#c = Dependencies()

#h = c.get_tdl("ça c'était l'autre")
#h = c.get_tdl("attends euh répète ta phrase")
#h = c.get_tdl("vision d'horreur c'était")
#h = c.get_tdl("pas bien en point quoi")
#h = c.get_tdl("ça doit être ça ouais")
#h = c.get_tdl("je vois pas le rapport")
#h = c.get_tdl("l'aubergine combat la pomme")

#h = c.get_tdl("moi je préfère la pomme")
#h = c.get_tdl("elle faisait peur tu trouves")