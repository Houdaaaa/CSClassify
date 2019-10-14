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
    def add_field(field):
        name = field.get_name()
        level = field.get_level()
        fieldNode = Node('Field', name=name, level=level) #id?
        graph.create(fieldNode)

    @staticmethod
    def add_question(question):
        title = question.get_title()
        answer = question.get_answer()
        questionNode = Node('Question', title=title, answer=answer)
        graph.create(questionNode)

    @staticmethod
    def add_subfield_relationship(field, subfield):
        fieldLevel = field.get_level()
        fieldName = field.get_name()
        subfieldLevel = subfield.get_level()
        subfieldName = subfield.get_name()

        if (fieldLevel < subfieldLevel):
            f1 = matcher.match("Field", name=fieldName).first()
            f2 = matcher.match("Field", name=subfieldName).first()
            graph.merge(Relationship(f1, 'subfield', f2))
        else:
            print("the level of the first param must be smaller than the level of the second")

    @staticmethod
    def add_is_linked_to_relationship(field1, field2):
        field1Level = field1.get_level()
        field1Name = field1.get_name()
        field2Level = field2.get_level()
        field2Name = field2.get_name()

        if(field1Level > field2Level):
            f1 = matcher.match("Field", name=field1Name, level=field1Level).first()
            f2 = matcher.match("Field", name=field2Name, level=field2Level).first()
            graph.merge(Relationship(f1, 'is_linked_to', f2))
        else:
            print("the level of the first param must be greater than the level of the second")

    @staticmethod
    def add_question_relationship(subfield, question):
        subfieldName = subfield.get_name()
        subfieldLevel = subfield.get_level()
        questionTitle = question.get_title()

        f = matcher.match("Field", name=subfieldName, level=subfieldLevel).first()
        q = matcher.match("Question", title=questionTitle).first()
        graph.merge(Relationship(f, 'subfield', q))

    '''return : object Node'''
    @staticmethod
    def find_one_field(name): #or param = object field?
            fieldNode = matcher.match("Field", name=name).first()
            return fieldNode

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
    def find_questions(field):
        fieldLevel = field.get_level()
        fieldName = field.get_name()

    '''delete the field and all its relationships'''
    @staticmethod
    def delete_field(field):        #supprime tous les noeuds ayant le même nom, utiliser id? corriger pour avoir field avec nom unique
        fieldLevel = field.get_level()
        fieldName = field.get_name()
        fieldNode = Database.find_one_field(fieldName)
        graph.delete(fieldNode)

    @staticmethod
    def delete_question(question):
        title = question.get_title()
        questionNode = matcher.match("Question", title=title).first()
        graph.delete(questionNode)

    @staticmethod
    def delete_relation(field1, field2, relationName):
        field1Name = field1.get_name()
        field1Level = field1.get_level()
        field2Name = field2.get_name()
        field2Level = field2.get_level()

        startNode= Database.find_one_field(field1Name)  #add levels?
        endNode= Database.find_one_field(field2Name)

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

    '''Attention je pars du principe qu'il y a au moins des sous-branches niveau 2 sinon don't display it'''
    @staticmethod
    def find_all_fields():
        levels_1_2 = graph.run('''MATCH (f:Field{level:1})-[:subfield]->(f2:Field) 
                                  RETURN f.name AS name, collect(f2.name) AS subfields''').data()

        levels_2_3 = graph.run('''MATCH (f:Field{level:1})-[:subfield]->(f2:Field)-[:subfield]->(f3:Field)
                                  RETURN f2.name AS name_L2, collect(f3.name) AS subfields_L3''').data()

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
        return allFields

    #def delete_subgraph
    #def add subgraph