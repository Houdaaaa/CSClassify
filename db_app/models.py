from neo4j import GraphDatabase, basic_auth

uri = "bolt://localhost:7687"
driver = GraphDatabase.driver(uri, auth=("neo4j", "editx"))

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

    def add_field(self, field):
        name = field.get_name()
        level = field.get_level()

        with driver.session() as session:
            cql_query = """CREATE (f:Field {name: '%s', level: '%d'})""" %(name, level)
            session.run(cql_query)

    def add_question(self, question):
        title = question.get_title()
        answer = question.get_answer()

        with driver.session() as session:
            cql_query = """CREATE (q:Question {title: '%s', answer: '%s'})""" %(title, answer)
            session.run(cql_query)

    def add_subfield_relationship(self, field, subfield):
        fieldLevel = field.get_level()
        fieldName = field.get_name()
        subfieldLevel = subfield.get_level()
        subfieldName = subfield.get_name()

        if (fieldLevel < subfieldLevel):
            with driver.session() as session:
                cql_query = """MATCH (f1: Field{name: '%s', level: '%d'})
                               MATCH (f2: Field{name: '%s', level: '%d'})
                               CREATE (f1)-[rel: subfield]->(f2)""" %(fieldName, fieldLevel, subfieldName, subfieldLevel)
                session.run(cql_query)
        else:
            print("the level of the first param must be smaller than the level of the second")

    def add_is_linked_to_relationship(self, field1, field2):
        field1Level = field1.get_level()
        field1Name = field1.get_name()
        field2Level = field2.get_level()
        field2Name = field2.get_name()

        if(field1Level > field2Level):
            with driver.session() as session:
                cql_query = """MATCH (f1: Field{name: '%s', level: '%d'})
                               MATCH (f2: Field{name: '%s', level: '%d'})
                               CREATE (f1)-[rel: is_linked_to]->(f2)""" %(field1Name, field1Level, field2Name, field2Level)
                session.run(cql_query)

        else:
            print("the level of the first param must be greater than the level of the second")

    def add_question_relationship(self, subfield, question):
        subfieldName = subfield.get_name()
        subfieldLevel = subfield.get_level()
        questionTitle = question.get_title()

        with driver.session() as session:
            cql_query = """MATCH (f: Field{name: '%s', level: '%d'})
                           MATCH (q: Question{title: '%s'})
                           CREATE (f)-[rel: question]->(q)""" % (subfieldName, subfieldLevel, questionTitle)
            session.run(cql_query)

    def find_one_field(self, name): #or param = object field?
        with driver.session() as session:
            cql_query = """MATCH (f: Field{name: '%s'}) RETURN f """ % (name)
            return session.run(cql_query)

    def find_subfields(self, field):
        fieldLevel = field.get_level()
        fieldName = field.get_name()

        with driver.session() as session:
            cql_query = """MATCH (f: Field{name: '%s', level: '%d'})-[rel: subfield*]->(f2: Field)
                           RETURN f2.name, f2.level""" % (fieldName, fieldLevel)
            return session.run(cql_query)

    def find_same_level_fields(self, level):
        with driver.session() as session:
            cql_query = """MATCH (f: Field{level: '%d'})
                           RETURN f.name""" % (level)
            return session.run(cql_query)

    def find_questions(self, field):
        fieldLevel = field.get_level()
        fieldName = field.get_name()
        with driver.session() as session:
            cql_query = """MATCH (f: Field{name: '%s', level: '%d'})-[rel: question]->(q: Question)
                           RETURN q.title""" % (fieldName, fieldLevel)
            return session.run(cql_query)

    def delete_field(self, field):
        fieldLevel = field.get_level()
        fieldName = field.get_name()

        with driver.session() as session:
            cql_query = """MATCH (f: Field{name: '%s', level: '%d'}) DETACH DELETE (f)""" % (fieldName, fieldLevel)
            return session.run(cql_query)

    def delete_question(self, question):
        title = question.get_title()

        with driver.session() as session:
            cql_query = """MATCH (q: Question{title: '%s'}) DETACH DELETE (q)""" % (title)
            return session.run(cql_query)

    def delete_relation(self, field1, field2, relationName):
        field1Name = field1.get_name()
        field1Level = field1.get_level()
        field2Name = field2.get_name()
        field2Level = field2.get_level()

        with driver.session() as session:
            cql_query = """MATCH (f1: Field{name: '%s', level: '%d'})-[rel:%s]->(f2: Field{name: '%s', level: '%d'})
                           DELETE (rel)""" % (field1Name, field1Level, relationName, field2Name, field2Level)
            return session.run(cql_query)

    def modify_field(self, field, newField): #modify the properties only
        fieldName = field.get_name()
        fieldLevel = field.get_level()
        newFieldName = newField.get_name()
        newFieldLevel = newField.get_level()

        with driver.session() as session:
            cql_query = """MATCH (f: Field{name: '%s', level: '%d'})
                           SET f.name = '%s', f.level = '%d'""" % (fieldName, fieldLevel, newFieldName, newFieldLevel)
            return session.run(cql_query)

    def modify_question(self, question, newQuestion):
        title = question.get_title()
        answer = question.get_answer()
        newTitle = newQuestion.get_title()
        newAnswer = newQuestion.get_answer()

        with driver.session() as session:
            cql_query = """MATCH (q: Question{title: '%s', answer: '%s'})
                           SET q.title = '%s', q.answer = '%s' """ % (title, answer, newTitle, newAnswer)
            return session.run(cql_query)

    #def delete_subgraph
    #def add subgraph