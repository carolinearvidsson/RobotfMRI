import spacy
import textdescriptives as td

nlp = spacy.load("fr_dep_news_trf")
nlp.add_pipe('textdescriptives')

class Dependencies:

    def get_tdl(self, utterance): # Utterance is a string where tokens are surrounded by black spaces
        unwanted = ['ah', 'euh', '***', 'ouais', 'oui', 'ok', 'non', 'voilà', '******', '*']
        print(utterance)
        for value in unwanted:
            if value in utterance.split():
                utterance = utterance.split()
                utterance.remove(value)
                utterance = ' '.join(utterance)
        doc = nlp(utterance)
        tdl = 0
        for token in doc:
            tdl += token._.dependency_distance['dependency_distance']
        return tdl

