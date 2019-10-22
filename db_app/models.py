from py2neo import Graph, Node, Relationship, NodeMatcher, matching

uri = "bolt://localhost:7687"
#graph = Graph(username='neo4j', password='editx')

graph = Graph(uri, user="neo4j", password="editx")
matcher = NodeMatcher(graph)


class Field():
    def __init__(self, name, level):
        self.name = name
        self.level = level

    def get_level(self):
        return self.level

    def get_name(self):
        return self.name

class Question():
    def __init__(self, title, answer):
        self.title = title
        self.answer = answer

    def get_title(self):
        return self.title

    def get_answer(self):
        return self.answer

class Database():   #classe statique?
    def __init__(self, password):
        self.password = password

    @staticmethod
    def add_field(field, level):
        '''name = field.get_name()
        level = field.get_level()'''
        fieldNode = Node('Field', name=field, level=level) #id?
        graph.create(fieldNode)

    @staticmethod
    def add_question(question):
        title = question.get_title()
        answer = question.get_answer()
        questionNode = Node('Question', title=title, answer=answer)
        graph.create(questionNode)

    @staticmethod
    def add_buzz_word(name):
        buzzWord = Node('BuzzWord', name=name)
        graph.create(buzzWord)

    @staticmethod
    def add_subfield_relationship(field, subfield):
        '''fieldLevel = field.get_level()
        fieldName = field.get_name()
        subfieldLevel = subfield.get_level()
        subfieldName = subfield.get_name()'''

        #if (fieldLevel < subfieldLevel):
        f1 = matcher.match("Field", name=field).first()
        f2 = matcher.match("Field", name=subfield).first()
        graph.merge(Relationship(f1, 'include', f2))
        #else:
        #    print("the level of the first param must be smaller than the level of the second")

    @staticmethod
    def add_is_linked_to_relationship(buzzWord, field):
        '''field1Level = field1.get_level()
        field1Name = field1.get_name()
        field2Level = field2.get_level()
        field2Name = field2.get_name()'''

        #if(field1Level > field2Level):
        f1 = matcher.match("BuzzWord", name=buzzWord).first()
        f2 = matcher.match("Field", name=field).first()
        graph.merge(Relationship(f1, 'is_linked_to', f2))
        #else:
        #    print("the level of the first param must be greater than the level of the second")

    @staticmethod
    def add_concerns_relationship(field1, field2):

        # if(field1Level > field2Level):
        f1 = matcher.match("Field", name=field1).first()
        f2 = matcher.match("Field", name=field2).first()
        graph.merge(Relationship(f1, 'concerns', f2))
        # else:
        #    print("the level of the first param must be greater than the level of the second")

    @staticmethod
    def add_question_relationship(subfield, question):
        #subfieldName = subfield.get_name()
        subfieldLevel = subfield.get_level()
        questionTitle = question.get_title()

        f = matcher.match("Field", name=subfield).first()
        q = matcher.match("Question", title=questionTitle).first()
        graph.merge(Relationship(f, 'question', q))

    '''return : object Node'''
    @staticmethod
    def find_one_field(name): #or param = object field?
            fieldNode = matcher.match("Field", name=name).first()
            return fieldNode

    @staticmethod
    def find_one_buzzword(name):  # or param = object field?
        buzzwordNode = matcher.match("BuzzWord", name=name).first()
        return buzzwordNode

    '''for questions and subfiels of a field'''     #attention juste pour un niveau, autre fonction pour trouver pour afficher tout le sous-graphe
    @staticmethod
    def find_sub_nodes(field, relationName):
        fieldLevel = field.get_level()
        fieldName = field.get_name()
        f = Database.find_one_field(fieldName)
        nodeList=[]
        for rel in graph.match((f,), r_type=relationName):
            nodeList.append(rel.end_node)   #type of rel.end_node = Node()
        #print(nodeList[0]['name']) #ok
        print(nodeList)
        return nodeList

    @staticmethod
    def find_sub_nodes_node(node, relationName):
        #f = Database.find_one_field(node['name'])
        nodeList = []
        for rel in graph.match((node,), r_type=relationName):
            nodeList.append(rel.end_node)  # type of rel.end_node = Node()
        # print(nodeList[0]['name']) #ok
        return nodeList

    @staticmethod
    def find_same_level_fields(level):
        fieldsNodes = matcher.match("Field", level=level)
        nodesList=[]
        for field in fieldsNodes:
            nodesList.append(field)
        #print(nodesList)
        return nodesList

    '''faut-t-il afficher les questions même pour un niveau 1?'''
    @staticmethod
    def find_buzz_words():
        fields = graph.run('''MATCH (f:BuzzWord)
                              WITH f
                              ORDER BY f.name
                              RETURN collect(f.name) AS names''').data()
        print(fields)
        return fields

    @staticmethod
    def find_buzz_word_fields(buzzword):
        #fields = Database.find_sub_nodes(buzzword, 'is_linked_to') str has no attribute field
        lev3 = graph.run('''MATCH (b: BuzzWord{name:{name}})-[:is_linked_to]->(f3: Field{level:3})<-[:include]-(f2: Field)
                               OPTIONAL MATCH (f2)<-[:include]-(f1:Field) 
                               WITH f2, f3, f1
                               ORDER BY f2.name
                               RETURN f2.name AS name, collect(f3.name) AS subfields, f1.name AS name_lev1
                               ORDER BY f1.name''', name=buzzword).data()

        lev1 = graph.run('''MATCH (b: BuzzWord{name:{name}})-[:is_linked_to]->(f1: Field{level:1})
                            RETURN f1.name AS name_lev1
                            ORDER BY f1.name''',name=buzzword).data()

        lev2 = graph.run('''MATCH (b: BuzzWord{name:{name}})-[:is_linked_to]->(f2: Field{level:2})<-[:include]-(f1: Field)
                            WITH f2, f1
                            ORDER BY f2.name
                            RETURN f2.name AS name, f1.name AS name_lev1
                            ORDER BY f1.name''', name=buzzword).data()  #autre moyen avec count() et -[:*1..3]-> pour plus d'extensibilité



        print('ok')
        print(lev3)
        finalList = []

        for field in lev1:
            finalDict = {}
            level1 = field['name_lev1']
            del field['name_lev1']
            finalDict['name'] = level1  # si la clé existe, donnée écrasée , non attention il y  aun append a faire
            finalDict['subfields'] = {}
            finalList.append(finalDict)

        for field in lev2:
            finalDict = {}
            level1 = field['name_lev1']
            del field['name_lev1']
            finalDict['name'] = level1  # si la clé existe, donnée écrasée , non attention il y  aun append a faire
            field['subfields'] = []
            finalDict['subfields'] = field
            finalList.append(finalDict)

        for field in lev3:
            finalDict = {}
            level1 = field['name_lev1']
            del field['name_lev1']
            finalDict['name'] = level1  #si la clé existe, donnée écrasée , non attention il y  aun append a faire
            #field['subfields'] = sorted(field['subfields']) #order list lev 3 --> ne sert plus car order by? test
            finalDict['subfields'] = field       #'subfields': {'name': 'process management', 'subfields': ['threads']}}
            finalList.append(finalDict)

        #order alphabetically lev 1
        sortedFinalList = sorted(finalList, key=lambda k: k['name'])
        # print(finalList) #liste de dico dont les clé sont des dico dont les clé sont des listes

        return sortedFinalList

    '''delete the field and all its relationships'''
    @staticmethod
    def delete_field(field):        #supprime tous les noeuds ayant le même nom, utiliser id? corriger pour avoir field avec nom unique
        fieldLevel = field.get_level()
        fieldName = field.get_name()
        fieldNode = Database.find_one_field(fieldName)
        graph.delete(fieldNode)

    '''delete the field and all its relationships'''

    @staticmethod
    def delete_buzz_word(buzzword):  # supprime tous les noeuds ayant le même nom, utiliser id? corriger pour avoir field avec nom unique
        fieldNode = Database.find_one_buzzword(buzzword)
        graph.delete(fieldNode)

    @staticmethod
    def delete_question(question):
        title = question.get_title()
        questionNode = matcher.match("Question", title=title).first()
        graph.delete(questionNode)

    @staticmethod
    def delete_relation(field1, field2, relationName):

        startNode= Database.find_one_field(field1)  #add levels?
        endNode= Database.find_one_field(field2) #name

        relationship = graph.match_one(nodes= (startNode, endNode), r_type=relationName)
        graph.separate(relationship)

    '''attention gérer l'existance du noeud 'field' avant le pushing'''
    @staticmethod
    def edit_field(field, newName, newLevel): #modify the properties only,
        fieldName = field.get_name()
        fieldLevel = field.get_level()

        fieldNode=Database.find_one_field(fieldName)

        fieldNode['name'] = newName
        fieldNode['level']= newLevel

        graph.push(fieldNode)



    @staticmethod
    def edit_question(question, newTitle, newAnswer):  #ou passer directement l'objet newQuestion?
        title = question.get_title()
        answer = question.get_answer()

        questionNode = matcher.match("Question", title=title).first()

        questionNode['title'] = newTitle
        questionNode['answer'] = newAnswer

        graph.push(questionNode)

    @staticmethod
    def find_questions(field):
        nameField = field.get_name()
        questions = graph.run('''MATCH (f:Field{name: {name}})-[:include*0..2]->(f2:Field)-[:question]->(q:Question)
                                 RETURN q.title AS title, q.answer AS answer 
                                 ORDER BY q.title''', name=nameField).data() #return list of dictionnaries

        return questions


    @staticmethod
    def find_subfields(nameField):
        fields = graph.run('''MATCH (f:Field{name:{name}})-[:include]->(f2:Field) 
                              OPTIONAL MATCH (f)-[:include]->(f2)-[:include]->(f3:Field)
                              WITH f2, f3
                              ORDER BY f3.name
                              RETURN f2.name AS name, collect(f3.name) AS subfields
                              ORDER BY f2.name''', name=nameField).data() #list of dico, [] if level 3


        '''# alphabetical order
        for x in fields:
            sortedList = sorted(x['subfields'])
            x['subfields'] = sortedList'''

        return fields

    @staticmethod
    def find_concerned_fields(nameField):
        fields = graph.run('''OPTIONAL MATCH (f:Field{name:{name}})-[:concerns]->(f2:Field) 
                              RETURN f2.name AS name
                              ORDER BY f2.name''',name=nameField).data()
        print(fields)
        return fields

    '''Attention je pars du principe qu'il y a au moins des sous-branches niveau 2 sinon don't display it'''
    @staticmethod
    def find_all_fields():
        levels_1_2 = graph.run('''MATCH (f:Field{level:1})-[:include]->(f2:Field) 
                                  WITH f, f2
                                  ORDER BY f2.name
                                  RETURN f.name AS name, collect(f2.name) AS subfields
                                  ORDER BY f.name''').data()

        levels_2_3 = graph.run('''MATCH (f:Field{level:1})-[:include]->(f2:Field)-[:include]->(f3:Field)
                                  WITH f2, f3
                                  ORDER BY f3.name
                                  RETURN f2.name AS name_L2, collect(f3.name) AS subfields_L3
                                  ORDER BY f2.name''').data()

        allFields = []
        for rootField in levels_1_2:
            rootFieldDict={}
            rootFieldDict["name"] = rootField['name']
            rootFieldDict["subfields"] = []
            fields_used = []
            for field_L2 in levels_2_3:
                if field_L2["name_L2"] in rootField['subfields']:  # rootField['subfields'] est une liste de str
                    subFieldDict = {}
                    subFieldDict["name"] = field_L2['name_L2']
                    subFieldDict["subfields"] = []
                    for field_L3 in field_L2['subfields_L3']:
                        subFieldDict["subfields"].append(field_L3)
                    rootFieldDict["subfields"].append(subFieldDict)
                    fields_used.append(field_L2['name_L2'])
            for field_L2_name in rootField['subfields']:  #pour level 2 qui n'ont pas de level 3, à refactorer
                if field_L2_name not in fields_used:
                    subFieldDict = {}
                    subFieldDict["name"] = field_L2_name
                    subFieldDict["subfields"] = []
                    rootFieldDict["subfields"].append(subFieldDict)
            allFields.append(rootFieldDict)

        # ordre alphabétique
        for x in allFields:
            sortedListOfDico = sorted(x["subfields"], key=lambda k: k['name'])   #sort a list of dico by key : name (level 2)
            x["subfields"] = sortedListOfDico
            '''for y in x["subfields"]:
                sortedList = sorted(y["subfields"])  #sort simply a list of strings (level 3)
                y["subfields"] = sortedList'''
        return allFields

    @staticmethod
    def create_database():
        dico=[
              {
                  'field': 'Computer systems', 'subfields':[
                      {'subfield':'mobiles', 'subsubfields':[]},
                      {'subfield':'embedded and cyber-physical systems', 'subsubfields':['sensor networks', 'robotic', 'sensors and actuators', 'system on chip', 'embedded systems']},
                      {'subfield': 'real-time systems', 'subsubfields':[]},
                      {'subfield': 'distributed systems', 'subsubfields':['cloud computing', 'computer cluster', 'grid computing']},
                      {'subfield': 'operating systems', 'subsubfields':[]}
                  ]
              },
              {
                  'field': 'Operating systems', 'subfields':[
                      {'subfield': 'protection & security', 'subsubfields':[]},
                      {'subfield': 'I/O systems', 'subsubfields': []},
                      {'subfield': 'architecture', 'subsubfields': ['monolytic', 'layered', 'VM based', 'micro-kernel', 'embedded', 'real-time', 'distributed']},
                      {'subfield': 'process management', 'subsubfields': ['process synchronization', 'deadlocks', 'threads', 'cpu scheduling']},
                      {'subfield': 'storage management', 'subsubfields': ['files systems', 'memory management']},
                      {'subfield': 'os types', 'subsubfields': ['Linux', 'Windows', 'Macos']},
                      {'subfield': 'mobile', 'subsubfields': ['IOS', 'Android', 'Windows']}
                  ]
              },
              {
                  'field': 'Programming', 'subfields':[
                      {'subfield': 'good practices', 'subsubfields': []},
                      {'subfield': 'compilers & interpreters', 'subsubfields': []},
                      {'subfield': 'languages', 'subsubfields': ['C', 'C++', 'C#', 'Java', 'PHP', 'Python', 'Ruby', 'SQL', 'JS', 'R', 'Go', 'Assembleur', '.NET', 'Shell', 'Delphi', 'Smalltalk', 'XML', 'HTML/CSS', 'TypeScript', 'Haskell', 'Groovy', 'Perl','VHDL', 'Xquery', 'Matlab', 'Kotlin', 'Scala', 'Swift']},
                      {'subfield': 'paradigms', 'subsubfields': ['imperative & derivatives', 'object-oriented', 'declarative & derivatives']},
                      {'subfield': 'frameworks', 'subsubfields': ['jQuery', 'AngularJS', 'ReactJS', 'Vue.js', 'Backbone', 'Symphonie', 'Laravel', 'Codeigniter', 'Zend', 'Spring', 'Hibernate', 'Hadoop', 'Spark', 'JSF', 'Django', 'Flask', 'ASP.NET', 'Meteor']}
                  ]
              },
              {
                  'field': 'Modeling, Design & Conception', 'subfields':[
                      {'subfield': 'software architectures', 'subsubfields': []},
                      {'subfield': 'software development methodologies & project management', 'subsubfields': []},
                      {'subfield': 'UML', 'subsubfields': ['diagrams', 'design patterns']},
                      {'subfield': 'good practices', 'subsubfields': []},
                      {'subfield': 'test & software quality', 'subsubfields': []},
                      {'subfield': 'version control & maintenance', 'subsubfields': []}
                  ]
              },
              {
                  'field': 'Visual computing', 'subfields':[
                      {'subfield': 'image analysis & processing', 'subsubfields': ['2D', '3D & more']},
                      {'subfield': 'virtual & augmented reality', 'subsubfields': []},
                      {'subfield': 'user ergonomy', 'subsubfields': ['UX', 'UI']}
                  ]
              },
              {
                  'field': 'Artificial intelligence', 'subfields':[
                      {'subfield': 'natural language processing', 'subsubfields': ['translation & speech', 'informations retrieval', 'language analysis']},
                      {'subfield': 'machine learning', 'subsubfields': ['neural networks and deep learning', 'predictive analytics']},
                      {'subfield': 'computer vision', 'subsubfields': ['machine vision', 'image processing and analysis']},
                      {'subfield': 'decision support systems', 'subsubfields': []}
                  ]
              },
              {
                  'field': 'Databases', 'subfields':[
                      {'subfield': 'ORM & ODM', 'subsubfields': []},
                      {'subfield': 'NoSQL DB models', 'subsubfields': ['column', 'key-value', 'document', 'graphs']},
                      {'subfield': 'relational DB models', 'subsubfields': []},
                      {'subfield': 'DBMS', 'subsubfields': ['SQLite', 'PostgreSQL', 'FireBird', 'MariaDB', 'Microsof SQL server', 'Microsoft access', 'Oracle']}
                  ]
              },
              {
                  'field': 'Security', 'subfields':[
                      {'subfield': 'systems security', 'subsubfields': []},
                      {'subfield': 'architecture & design security', 'subsubfields': []},
                      {'subfield': 'networks security', 'subsubfields': ['firewalls', 'router-switch security', 'intrusion detection & prevention systems', 'Email filtering']},
                      {'subfield': 'cryptography', 'subsubfields': []},
                      {'subfield': 'identify & access management', 'subsubfields': ['authentification & identification', 'access management']},
                      {'subfield': 'business compliance', 'subsubfields': ['business continuity plan & procedures', 'compliance']}
                  ]
              },
              {
                  'field': 'Network & telecommunication', 'subfields':[
                      {'subfield': 'networks architectures', 'subsubfields': ['topologies', 'design principles']},
                      {'subfield': 'network equipment', 'subsubfields': ['fiber', 'bridges&switches', 'routers', 'adapters & repeaters', 'physical firewalls']},
                      {'subfield': 'wireless & mobile telecommunication', 'subsubfields': []},
                      {'subfield': 'network administration', 'subsubfields': ['network cabling', 'routing management', 'security management', 'access rights management']},
                      {'subfield': 'services', 'subsubfields': ['API', 'cloud computing']},
                      {'subfield': 'network protocols', 'subsubfields': []}
                  ]
              },
              {
                  'field': 'Software', 'subfields':[
                      {'subfield': 'software development', 'subsubfields': []},
                      {'subfield': 'mobile development', 'subsubfields': []},
                      {'subfield': 'ERP&CRM', 'subsubfields': []},
                      {'subfield': 'CMS', 'subsubfields': []},
                      {'subfield': 'computer graphics & animations', 'subsubfields': []},
                      {'subfield': 'gaming development', 'subsubfields': []},
                      {'subfield': 'libraries', 'subsubfields': []},
                      {'subfield': 'CAD', 'subsubfields': []}
                  ]
              }
        ]

        for field in dico:
            Database.add_field(field['field'], 1)
            for subfield in field['subfields']:
                Database.add_field(subfield['subfield'], 2)
                Database.add_subfield_relationship(field['field'], subfield['subfield'])
                for subsubfield in subfield['subsubfields']:
                    Database.add_field(subsubfield, 3)
                    Database.add_subfield_relationship(subfield['subfield'], subsubfield)

    #def delete_subgraph
    #def add subgraph