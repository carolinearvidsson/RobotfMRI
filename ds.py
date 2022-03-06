class DataStructure:
    def __init__(self, transfiles):
        transfiles.sort()
        self.structure = {} # Nested dict with following structure {subject id (S01-S25): session(1-4):\
                                    # conversation(01-06): [textgrid filename, textgrid filename]}
        for p in transfiles:
            i = p.split('_')
            id = i[0].lower()
            session = i[1][-1]
            conversation = i[3][-1]
            if id not in self.structure:
                self.structure[id] = {}
            if session not in self.structure[id]:
                self.structure[id][session] = {} 
            self.structure[id][session].setdefault(conversation, []).append(p)




