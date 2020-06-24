from py2neo import Graph, Node, Relationship, NodeMatcher
import json
from flask import Flask
from flask_pymongo import PyMongo, ObjectId
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)

app.config['MONGO_URI'] = 'mongodb://127.0.0.1:27017/csclassify'

# connection to the MongoDB database
mongo = PyMongo(app)

# To use extension flask-login
login = LoginManager(app)
login.login_view = 'login'

# connection to the neo4j database
uri = "bolt://localhost:7687"
graph = Graph(uri, user="neo4j", password="editx")

#  Node matcher initialization
matcher = NodeMatcher(graph)


class User:

    """ This class concern "Flask-login" module.
    It about user acccount management. """

    def __init__(self, username):
        self.username = username
        self.lastname = ''
        self.firstname = ''
        self.email = ''
        self.job = ''
        self.website_url = ''
        self.graphs_id = []
        self.id = ''

    @staticmethod
    def is_authenticated():
        return True

    @staticmethod
    def is_active():
        return True

    @staticmethod
    def is_anonymous():
        return False

    def get_id(self):
        return self.username

    @staticmethod
    def check_password(password_hash, password):
        return check_password_hash(password_hash, password)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def get_id_2(self):
        return self.id

    def set_id_2(self, id):
        self.id = id

    @login.user_loader  #
    def load_user(username):

        """ Flask-login also requires you to define a “user_loader” function which, given a user ID,
        returns the associated user object.

        :return: the associated user object """

        u = mongo.db.Users.find_one({"username": username})
        if not u:
            return None
        user_obj = User(username=u['username'])
        user_obj.set_var(lastname=u['lastname'], firstname=u['firstname'], email=u['email'], job=u['job'],
                         website_url=u['website_url'], graphs_id=u['graphs_id'], id=u['_id'])
        user_obj.set_password(password=u['password'])
        return user_obj

    def get_username(self):
        return self.username

    def set_username(self, username):
        self.username = username

    def get_lastname(self):
        return self.lastname

    def set_lastname(self, lastname):
        self.lastname = lastname

    def get_firstname(self):
        return self.firstname

    def set_firstname(self, firstname):
        self.firstname = firstname

    def get_email(self):
        return self.email

    def set_email(self, email):
        self.email = email

    def get_job(self):
        return self.job

    def set_job(self, job):
        self.job = job

    def get_website_url(self):
        return self.website_url

    def set_website_url(self, website_url):
        self.website_url = website_url

    def get_graphs_id(self):
        return self.graphs_id

    def set_graphs_id(self, id_list):  # uuid: list of strings
        self.graphs_id = id_list

    def add_graphs_id(self, id):
        self.graphs_id.append(id)

    def set_var(self, lastname, firstname, email, job, website_url, graphs_id, id):
        self.set_lastname(lastname)
        self.set_firstname(firstname)
        self.set_email(email)
        self.set_job(job)
        self.set_website_url(website_url)
        self.set_graphs_id(graphs_id)
        self.set_id_2(id)

    def convert_to_doc(self):

        """ Convert the user object to a dictionary

        :return: dictionary with informations about the user """

        doc = {
            'lastname': self.lastname,
            'firstname': self.firstname,
            'email': self.email,
            'job': self.job,
            'website_url': self.website_url,
            'username': self.username,
            'password': self.password_hash
        }

        return doc


class MongoDB:

    """ This class concern request to the mongoDB database  """

    user_collection = mongo.db.Users
    classification_collection = mongo.db.Classification

    @staticmethod
    def add_classification(classification):

        """ Add classification to mongoDB

        :param classification: informations about the classification
        :return: uuid of the classification """

        req = mongo.db.Classification.insert_one(classification)
        uuid = str(req.inserted_id)
        Database.add_classification_2(uuid)

        return uuid

    @staticmethod
    def delete_classification(uuid_classification):

        """ Delete a classification

        :param uuid_classification: uuid of the classification
        :return: uuid of the deleted classification """

        uuid = ObjectId(uuid_classification)
        req = mongo.db.Classification.delete_one({'_id': uuid})
        Database.delete_classification(uuid_classification)
        return uuid

    @staticmethod
    def find_all_classifications_names():

        """ Find the name of all classification existing in the mongoDB

        :return: dictionary with all classifications names """

        req = mongo.db.Classification.find({}, {'name': 1, '_id': 0})  # order by c.name    print(req[0]['name'])
        names = req.sort('name')
        return req

    @staticmethod
    def find_classifications_names(user_id):  # id_graphs = list of ints -- must be objectId

        """ Find the names of the classification that the user has created

        :param user_id: the uuid of the user
        :return: dictionary with all classification names created by the user """

        req = mongo.db.Classification.find({'user_id': user_id}, {'_id': 0, 'name': 1})  # censé être un ObjectID
        names = req.sort('name')

        return names

    @staticmethod
    def find_classification_info(name):

        """ Find all information about one classification

        :param name: the name of the classification
        :return: All information about the classification """

        infos = mongo.db.Classification.find_one({'name': name}, {'_id': 1, 'user_id': 1})
        return infos

    @staticmethod
    def find_classification_name(uuid_classification):

        """ Find the name of a classification given the uuid

        :param uuid_classification: uuid of the classification
        :return: the name of the classification """

        info = mongo.db.Classification.find_one({'_id': ObjectId(uuid_classification)}, {'_id': 0, 'name': 1})
        print(info)
        return info['name']


class Database:

    """ This class concern all Neo4j DB requests."""

    @staticmethod
    def cloning_check(uuid_classification):  # when fork

        """Real clone from ancestor classification

        :param uuid_classification: uuif of the classification choosed
        :return: 0 """

        is_cloned = graph.run('''
                        MATCH (c:Classification{uuid:{uuid_classification}})
                        WITH c
                        WHERE EXISTS(c.is_cloned) 
                        MATCH (c)-[:forked_from]->(c2:Classification)
                        RETURN c.is_cloned AS is_cloned, c2.uuid
                    ''', uuid_classification=uuid_classification).data()
        print(is_cloned)

        if is_cloned != []:
            if is_cloned[0]['is_cloned'] == True:
                return 1  # pass

        #  Check if there is an ancestor classification
        classification_to_clone = graph.run('''
                        OPTIONAL MATCH(c:Classification{uuid:{uuid_classification}})-[:forked_from]->(c2:Classification)
                        WHERE EXISTS (c2.uuid)
                        RETURN c2.uuid AS uuid''',
                                            uuid_classification=uuid_classification).data()  # list of 1 dico [{'uuid': None}]

        classification_to_clone2 = graph.run('''
                        OPTIONAL MATCH(c:Classification{uuid:{uuid_classification}})<-[:forked_from]-(c2:Classification) 
                        WHERE EXISTS (c2.uuid)
                        RETURN c2.uuid AS uuid''',
                                             uuid_classification=uuid_classification).data()  # list of multiples dico [{'uuid': None},]

        if classification_to_clone[0]['uuid'] != None:  # one classification is possible --> ancestor
            Database.clone_subgraph(classification_to_clone[0]['uuid'], uuid_classification)

        if classification_to_clone2 != None:  # multiples classifications are possibles
            for classification in classification_to_clone2:
                req = graph.run('''
                            MATCH (c:Classification{uuid:{uuid_classification}})
                            WITH c
                            WHERE EXISTS(c.is_cloned)
                            MATCH (c)-[:forked_from]->(c2:Classification)
                            RETURN c.is_cloned, c2.uuid AS uuid
                            ''', uuid_classification=classification['uuid']).data()
                if not req:  # if list is empty so if is_cloned variable doesn't exists
                    Database.clone_subgraph(uuid_classification, classification['uuid'])
                    #  Dans le cas où c lui qui a été cloné
        return 0

    @staticmethod
    def clone_subgraph(uuid_classification_to_clone, uuid_clone):

        """ Clone a subgraph

        :param uuid_classification_to_clone: uuid of the classification to clone
        :param uuid_clone: uuid of the clone """

        req = graph.run('''
                    MATCH  (rootA:Classification{uuid:{uuid_classification_to_clone}}),
                           (rootB:Classification{uuid:{uuid_clone}})
                    CALL apoc.path.subgraphAll(rootA, {relationshipFilter:'include>'})
                    YIELD nodes, relationships
                    CALL apoc.refactor.cloneSubgraph(
                        nodes,
                        [rel in relationships WHERE type(rel) = 'include'],
                        { standinNodes:[[rootA, rootB]],
                          skipProperties:['uuid']})  
                    YIELD input, output, error
                    RETURN input, output, error
                    ''', uuid_classification_to_clone=uuid_classification_to_clone, uuid_clone=uuid_clone).data()

        # add property "is_cloned"
        Database.add_is_cloned_property(uuid_clone)

        return req



    @staticmethod
    def add_classification_2(uuid):

        """Add a Node "Classification"

        :param uuid: The uuid of the classification"""

        classification_node = Node('Classification',
                                   uuid=uuid)
        graph.create(classification_node)

    @staticmethod
    def delete_classification(uuid_classification):

        """Deletes the classification and all its relationships

            :param uuid_classification: the unique id of the classification to delete"""

        graph.run('''MATCH (c:Classification{uuid:{uuid_classification}})
                     CALL apoc.path.subgraphAll(c, {relationshipFilter:'include>'})
                     YIELD nodes, relationships
                     UNWIND nodes AS n
                     DETACH DELETE n
                     DETACH DELETE c
                     RETURN 1''', uuid_classification=uuid_classification)

    @staticmethod
    def add_field(field, level, origin_field, uuid_classification):

        """adds a field in a specific classification to the database

            :param field: the name of the field
            :param level: the relationship level of the field
            :param relation: the relationship wanted
            :param origin_field: the uuid of the field to which to add another field
            :param uuid_classification: the specific classification """

        request = graph.run("""MATCH (c:Classification{uuid:{uuid_classification}})-[:include*1..4]->(f1:Field{uuid:{origin_field}}) 
                              WITH f1 
                              CREATE (f2:Field{name:{name}, level:{level}})
                              CREATE (f1)-[:include]->(f2)""", uuid_classification=uuid_classification,
                            origin_field=origin_field, name=field, level=level)

        # field_node = Node('Field', name=field, level=level)
        # graph.create(field_node)

    @staticmethod
    def add_root_field(field, uuid_classification):  # level = 1 always

        """Adds a field to the database

            :param field: the name of the field
            :param level: the relationship level of the field"""

        graph.run('''MATCH (c:Classification{uuid:{uuid}})
                     CREATE (f:Field{name:{name}, level:1})<-[:include]-(c)''', uuid=uuid_classification,
                  name=field).data()

    @staticmethod
    def add_subgraph(root_name, fields, uuid_classification):

        """Add a subgraph to a classification

        :param uuid_classification: The uuid of the classification
        :param root_name: The name of the root of the sybgraph (so the field with level = 1)
        :param fields: All fields that define the subgraph"""

        field_l2 = fields['level2']
        fields_l3 = fields['level3']

        graph.run('''MATCH (f1:Field{name:{root_name}})<-[:include]-(c:Classification{uuid:{uuid}})
                     CREATE (f2:Field{name:{field_l2}, level:2})<-[:include]-(f1)''',
                  uuid=uuid_classification,
                  root_name=root_name,
                  field_l2=field_l2).data()

        for f in fields_l3:
            graph.run('''MATCH (f2:Field{name:{field_l2}, level:2})
                         CREATE (f3:Field{name:{f}, level:3})<-[:include]-(f2)''', field_l2=field_l2,
                      f=f).data()

    @staticmethod
    def add_question(title, url):

        """adds a question to the database

            :param title: the title of the question
            :param url: the url that redirects to the question located on EDITx site"""

        question_node = Node('Question', title=title, url=url)
        graph.create(question_node)

    @staticmethod
    def add_buzz_word(name):

        """add a field to the database

            :param name: the name of the buzz word"""

        buzz_word = Node('BuzzWord', name=name)
        graph.create(buzz_word)

    @staticmethod
    def add_classification(name):

        """ Add a classification to te DB using the name
        (Don't use it)

        :param name: The name of the classification
        :return: The uuid of the classification """

        classification_node = Node('Classification', name=name)
        graph.create(classification_node)

        uuid = graph.run('''MATCH (c: Classification{name:{name}})  
                            RETURN c.uuid AS uuid''',
                         name=name).data()
        print(uuid)
        return uuid[0]['uuid']

    @staticmethod
    def add_subclassification_relationship(classification_id, l1_fields_list):

        """ Add relationship "include" between fields

        :param classification_id: The uuid of the concerned classification
        :param l1_fields_list: List of fields names which are fields of the classification """

        f1 = matcher.match("Classification", uuid=classification_id).first()  # au lieu du name : id?

        for field in l1_fields_list:
            f2 = matcher.match("Field", name=field).first()  # id au lieu de field['name']?
            graph.merge(Relationship(f1, 'include', f2))

    @staticmethod
    def add_translation(field, translated_field, language, uuid_classification):

        """Add a translation of a field of a classification

        :param field: the field to translate
        :param translated_field: the translation of the field
        :param language: the language of translation
        :param uuid_classification: The uuid of the concerned classification"""

        req = graph.run('''MATCH (c:Classification{uuid:{uuid_classification}})-[:include*1..4]->(f1:Field {name:{field}})
                           CREATE (f1)-[:translate_into{language:{language}}]->(f2:Field {name:{translated_field}})''',
                        field=field, translated_field=translated_field, language=language,
                        uuid_classification=uuid_classification)
        return req

    @staticmethod
    def add_fork_relationship(classification_uuid, ancestor_uuid):

        """adds a relationship between a field and its subfield to the database

            :param ancestor: the id of the source classification
            :param classification: the id of the new classification """

        f1 = matcher.match("Classification", uuid=classification_uuid).first()
        f2 = matcher.match("Classification", uuid=ancestor_uuid).first()
        graph.merge(Relationship(f1, 'forked_from', f2))

    @staticmethod
    def add_subfield_relationship(field, subfield):

        """adds a relationship between a field and its subfield to the database

            :param field: the name of the field
            :param subfield: the name of the subfield"""

        # if (fieldLevel < subfieldLevel):
        f1 = matcher.match("Field", name=field).first()
        f2 = matcher.match("Field", name=subfield).first()
        graph.merge(Relationship(f1, 'include', f2))
        # else:
        #    print("the level of the first param must be smaller than the level of the second")

    @staticmethod
    def add_is_linked_to_relationship(buzzword, field):

        """adds a relationship between a field and its subfield to the database

            :param buzzword: the name of the buzz word
            :param field: the name of the field linked to the buzz word"""

        # if(field1Level > field2Level):
        f1 = matcher.match("BuzzWord", name=buzzword).first()
        f2 = matcher.match("Field", name=field).first()
        graph.merge(Relationship(f1, 'is_linked_to', f2))
        # else:
        #    print("the level of the first param must be greater than the level of the second")

    @staticmethod
    def add_concerns_relationship(field1, field2):

        """add a relationship between a field and its subfield to the database

            :param field1: the name of the field
            :param field2: the name of the field linked to the field1"""

        # if(field1Level > field2Level):
        f1 = matcher.match("Field", name=field1).first()
        f2 = matcher.match("Field", name=field2).first()
        graph.merge(Relationship(f1, 'concerns', f2))
        # else:
        #    print("the level of the first param must be greater than the level of the second")

    @staticmethod
    def add_question_relationship(subfield, question_title):

        """adds a relationship between a field and its subfield to the database

            :param subfield: the name of the field
            :param question_title: the title of the question linked to the subfield"""

        f = matcher.match("Field", name=subfield).first()
        q = matcher.match("Question", title=question_title).first()
        graph.merge(Relationship(f, 'question', q))

    @staticmethod
    def find_one_field(name):

        """finds a field in the database by its name

            :param name: the name of the field
            :returns: the field searched as a node object"""

        field_node = matcher.match("Field", name=name).first()
        return field_node

    @staticmethod
    def find_one_buzzword(name):

        """finds a buzz word in the database by its name

            :param name: the name of the buzz word
            :returns: the buzz word searched as a node object"""

        buzzword_node = matcher.match("BuzzWord", name=name).first()
        return buzzword_node


    @staticmethod
    def find_sub_nodes(field_name, relationName):

        """finds the subnodes of a field with the desired relationship

            :param field_name: the name of the field
            :param relationName: the name of the desired relationship
            :returns: a list of all subnodes of the field concerned by the relationship wished"""

        f = Database.find_one_field(field_name)
        node_list = []
        for rel in graph.match((f,), r_type=relationName):
            node_list.append(rel.end_node)  # type of "rel.end_node" : Node
        return node_list

    @staticmethod
    def find_same_level_fields(level, uuid_classification):

        """finds all fields that have the same level in the classification

            :param level: the desired level
            :returns: a list of all fields that have the desired level"""

        fields = graph.run('''MATCH ((c:Classification{uuid:{uuid_classification}})-[:include*]->(f:Field{level:{level}}))
                                      WITH f
                                      ORDER BY f.name
                                      RETURN f.name AS name, f.uuid AS uuid''',
                           uuid_classification=uuid_classification, level=level).data()

        return fields

    @staticmethod
    def find_root_fields(uuid_classification):

        """Find the fields with level=1 of a classification

        :param uuid_classification: The uuid of the concerned classification
        :return: The root fields """

        fields = graph.run('''MATCH ((c:Classification{uuid:{uuid_classification}})-[:include]->(f:Field{level:1}))
                              WITH f
                              ORDER BY f.name
                              RETURN f.name AS name, f.uuid AS uuid''', uuid_classification=uuid_classification).data()
        return fields

    @staticmethod
    def find_level(field_uuid):

        """ Find the level of a field

        :param field_uuid: The uuid of the concerned field
        :return: The level of this field """

        level = graph.run('''MATCH (f:Field{uuid:{field_uuid}})
                              RETURN f.level AS level''', field_uuid=field_uuid).data()
        return level[0]['level']

    @staticmethod
    def find_fields(root_id):

        """Find all field of a root field

        :param root_id: The uuid of the concerned root_field
        :return: All subfields of the root_field"""

        fields = graph.run('''MATCH (f:Field{level:1, uuid:{root_id}})-[:include*1..2]->(f2:Field)
                              WITH f2
                              ORDER BY f2.name
                              RETURN f2.name AS name, f2.uuid AS uuid''', root_id=root_id).data()
        return fields

    @staticmethod
    def find_name(uuid_field):

        """ Find the name of a field

        :param uuid_field: the uuif of the concerned field
        :return: The name of this field"""

        field = graph.run('''MATCH (f:Field{uuid:{uuid_field}})
                             RETURN f.name AS name''', uuid_field=uuid_field).data()
        return field[0]['name']

    @staticmethod
    def find_rel(field1, field2):

        """ Find the type of the relationship between two fields.
            Beware, direction is important.

        :param field1: First field
        :param field2: Second field
        :return: The name of the relationship between these two fields """

        rel = graph.run('''MATCH (f1:Field{uuid:{field1}})-[r]->(f2:Field{uuid:{field2}})
                               RETURN type(r) AS type''', field1=field1, field2=field2).data()
        return rel  # rel[0]['type']

    @staticmethod
    def find_all_fieldss(uuid_classification):

        """Find all fields of a classification

        :param uuid_classification: the uuid of the concerned classification
        :return: All fields of the classification"""
        fields = graph.run('''MATCH (c:Classification{uuid:{uuid_classification}})-[:include*1..4]->(f:Field)
                              WITH f
                              ORDER BY f.name
                              RETURN f.name AS name, f.uuid AS uuid''', uuid_classification=uuid_classification).data()
        return fields

    @staticmethod
    def find_buzz_words():

        """finds all buzz words

            :returns:  a dictionary with as key 'names' and as value a list with all buzz words"""

        fields = graph.run('''MATCH (f:BuzzWord)
                              WITH f
                              ORDER BY f.name
                              RETURN collect(f.name) AS names''').data()
        return fields

    @staticmethod
    def find_buzz_word_fields(buzzword):

        """finds the fields (and the fields that include them ) linked to the desired buzz word

            :param buzzword: the desired level
            :returns: a list of dictionaries that represent the fields (and the fields that include them ) linked to
                        the desired buzz word
                      --> list of dictionaries whose key values are dictionaries whose key values are lists"""

        lev3 = graph.run('''MATCH (b: BuzzWord{name:{name}})-[:is_linked_to]->(f3: Field{level:3})<-[:include]-(f2: Field)
                               OPTIONAL MATCH (f2)<-[:include]-(f1:Field) 
                               WITH f2, f3, f1
                               ORDER BY f2.name
                               RETURN f2.name AS name, collect(f3.name) AS subfields, f1.name AS name_lev1
                               ORDER BY f1.name''', name=buzzword).data()

        lev1 = graph.run('''MATCH (b: BuzzWord{name:{name}})-[:is_linked_to]->(f1: Field{level:1})
                            RETURN f1.name AS name_lev1
                            ORDER BY f1.name''', name=buzzword).data()

        lev2 = graph.run('''MATCH (b: BuzzWord{name:{name}})-[:is_linked_to]->(f2: Field{level:2})<-[:include]-(f1: Field)
                            WITH f2, f1
                            ORDER BY f2.name
                            RETURN f2.name AS name, f1.name AS name_lev1
                            ORDER BY f1.name''', name=buzzword).data()

        # Construction of a list of dictionaries whose key values are dictionaries whose key values are lists
        final_list = []

        for field in lev1:
            final_dict = {}
            level1 = field['name_lev1']
            del field['name_lev1']
            final_dict['name'] = level1
            final_dict['subfields'] = {}
            final_list.append(final_dict)

        for field in lev2:
            final_dict = {}
            level1 = field['name_lev1']
            del field['name_lev1']
            final_dict['name'] = level1
            field['subfields'] = []
            final_dict['subfields'] = field
            final_list.append(final_dict)

        for field in lev3:
            final_dict = {}
            level1 = field['name_lev1']
            del field['name_lev1']
            final_dict['name'] = level1
            final_dict['subfields'] = field  # ex: 'subfields': {'name': 'process management','subfields': ['threads']}}
            final_list.append(final_dict)

        # order alphabetically the level 1
        sorted_final_list = sorted(final_list, key=lambda k: k['name'])

        return sorted_final_list

    @staticmethod
    def delete_field(uuid_field):

        """Deletes the field and all its relationships/subnodes

            :param uuid_field: the uuid of the field to delete"""


        req = graph.run('''MATCH (f:Field{uuid:{uuid_field}})
                     CALL apoc.path.subgraphAll(f, {relationshipFilter:'include>|concerns>'})
                     YIELD nodes, relationships
                     UNWIND nodes AS n
                     DETACH DELETE n
                     DETACH DELETE f
                     RETURN 1''', uuid_field=uuid_field)
        return req

    @staticmethod
    def delete_buzz_word(buzzword):

        """Deletes the buzz word and all its relationships

            :param buzzword: the name of the buzz word to delete"""

        field_node = Database.find_one_buzzword(buzzword)
        graph.delete(field_node)

    @staticmethod
    def delete_question(question_title):

        """Deletes the question and all its relationships

            :param question_title: the title of the question to delete"""

        question_node = matcher.match("Question", title=question_title).first()
        graph.delete(question_node)

    @staticmethod
    def add_is_cloned_property(uuid_classification):

        """Add 'is_cloned' property of a field

            :param uuid_classification: the uuid of the concerned classification """

        req = '''MATCH (c:Classification{uuid:{uuid_classification}})
                        SET c.is_cloned = True'''
        graph.run(req, uuid_classification=uuid_classification)

        return 0

    @staticmethod
    def edit_field(uuid_field, new_name):

        """Edits the properties of a field

            :param uuid_field: the uuid of the field to edit
            :param new_name: the new name of the field"""

        req = graph.run("""MATCH(f:Field{uuid:{uuid_field}}) SET f.name={new_name}""", uuid_field=uuid_field,
                        new_name=new_name)
        return req

    @staticmethod
    def edit_field_request(uuid_field, name):

        """Generate the query that is used to edit a field

        :param uuid_field: the uuid of the concerned field
        :param name: the new name of this field"""

        request = "MATCH (f:Field{uuid:" + uuid_field + "}) SET f.name=" + name
        return request

    @staticmethod
    def add_field_request(name, level, relation, origin_field, uuid_classification):

        """Generate the query that is used to create a field

        :param name: The name of the new field
        :param level: the level of the new field
        :param relation: the type of the relationship between the new field and the origin field
        :param origin_field: the field linked to the new field
        :param uuid_classification: the uuid of the concerned classification
        :return:the query to add this new field to the database """
        request = "MATCH (c:Classification{uuid: " + uuid_classification + "}})-[:include*1..4]->(f1:Field{uuid:" + origin_field + "}) " \
                                                                                                                                  "WITH f1 " \
                                                                                                                                  "CREATE (f2:Field{name:" + name + ", level:" + level + "})" \
                                                                                                                                                                                         "CREATE (f1)-[r:" + relation + "]->(f2)"
        # Beware ! name & uuid properties in str
        return request

    @staticmethod
    def edit_rel_request(uuid_field1, uuid_field2, old_relation, new_relation):

        """Generate the query that is used to edita relationship

        :param uuid_field1: origin field
        :param uuid_field2: end field
        :param old_relation: old relation
        :param new_relation: the new relation
        :return: the query to edit a relationship between uuid_field1 and uuid_field2 """

        request = "MATCH (f1:Field{uuid:" + uuid_field1 + "})-[r:" + old_relation + "]->(f2:Field{uuid:" + uuid_field2 + "}) " \
                 "WITH r, f1, f2 " \
                 "DELETE r " \
                 "CREATE (f1)-[r:" + new_relation + "]->(f2)"
        # attention propriété name et uuid en string

        return request

    @staticmethod
    def edit_rel(uuid_field1, uuid_field2, old_relation, new_relation):

        """Edit a relationship between uuid_field1 and uuid_field2

        :param uuid_field1: origin field
        :param uuid_field2: end field
        :param old_relation: old relation
        :param new_relation: the new relation """

        req = graph.run("""MATCH (f1:Field{uuid:{uuid_field1}})-[r:"""+old_relation+"""]->(f2:Field{uuid:{uuid_field2}})
                            WITH r, f1, f2
                            DELETE r 
                            CREATE (f1)-[r2:""" + new_relation + """]->(f2)""",
                        uuid_field1=uuid_field1, uuid_field2=uuid_field2)
        return req

    @staticmethod
    def add_rel_request(uuid_field1, uuid_field2, new_relation, uuid_classification):

        """Generate the query that is used to add a relationship between uuid_field1 and uuid_field2

        :param uuid_field1: origin field
        :param uuid_field2: end field
        :param old_relation: old relationship
        :param new_relation: the new relationship
        :return:the query that is used to add a relationship between uuid_field1 and uuid_field2"""

        request = "MATCH (c:Classification{uuid:"+ uuid_classification +"}})-[:include*1..4]->(f1:Field{uuid:" + uuid_field1 + "})" \
                  "MATCH (f2:Field{uuid:" + uuid_field2 + "}) " \
                  "WITH f1, f2"\
                   "CREATE (f1)-[r:" + new_relation + "]->(f2)"
        # Beware, name & uuid properties in str

        return request

    @staticmethod
    def add_relation(uuid_field1, uuid_field2, new_relation, uuid_classification):

        """Add a relationship between uuid_field1 and uuid_field2

        :param uuid_field1: origin field
        :param uuid_field2: end field
        :param old_relation: old relationship
        :param new_relation: the new relationship"""

        req = graph.run("""MATCH (c:Classification{uuid:{uuid_classification}})-[:include*1..4]->(f1:Field{uuid:{uuid_field1}})
                     MATCH (c:Classification{uuid:{uuid_classification}})-[:include*1..4]->(f2:Field{uuid:{uuid_field2}})
                     WITH f1, f2
                     CREATE (f1)-[:"""+new_relation+"""]->(f2)
                    """, uuid_classification=uuid_classification, uuid_field1=uuid_field1, uuid_field2=uuid_field2)
        return req

    @staticmethod
    def delete_relation_request(uuid_field1, uuid_field2, relation_name):

        """Request that deletes the relationship between 2 fields

            :param field1: the name of one of the two fields
            :param field2: the name of the other field
            :param relation_name: the relationship between the two fields"""

        # Be carreful to check the existence of the nodes

        request = "MATCH (f1:Field{uuid:" + uuid_field1 + "})-[r:" + relation_name + "]->(f2:Field{uuid:" + uuid_field2 + "}) " \
                  "DELETE r "
        return request

    @staticmethod
    def delete_relation(uuid_field1, uuid_field2, relation_name):

        """Deletes the relationship between 2 fields

            :param uuid_field1: the uuid of one of the two fields
            :param uuid_field2: the uuid of the other field
            :param relation_name: the relationship between the two fields"""

        request = graph.run("""MATCH (f1:Field{uuid:{uuid_field1}})-[r:""" + relation_name + """]->(f2:Field{uuid:{uuid_field2}})
                               DELETE r """, uuid_field1=uuid_field1, uuid_field2=uuid_field2)
        return request



    @staticmethod
    def delete_field_request(uuid_field):

        """Generate query that is used to delete a field

        :param uuid_field: the uuid of the concerned field
        :return: the query that delete the field"""

        request = "MATCH (f:Field{uuid:" + uuid_field + "}) " \
                  "CALL apoc.path.subgraphAll(f, {relationshipFilter:'include>|concerns>'})" \
                  "YIELD nodes, relationships"\
                  "UNWIND nodes AS n"\
                  " DETACH DELETE n"\
                  "DETACH DELETE f"\
                  "RETURN 1"
        return request

    @staticmethod
    def edit_question(title, new_title, new_url):

        """Edits the properties of a question

            :param title: the name of the question to edit
            :param new_title: the new title of the question
            :param new_url: the new url of the question"""

        question_node = matcher.match("Question", title=title).first()

        question_node['title'] = new_title
        question_node['url'] = new_url

        graph.push(question_node)

    @staticmethod
    def find_questions(field_name):

        """finds all questions linked to a field

            :param field_name: the name of the field
            :returns: a list of dictionaries that represent all questions linked to the field"""

        questions = graph.run('''MATCH (f:Field{name: {name}})-[:include*0..2]->(f2:Field)-[:question]->(q:Question)
                                 RETURN q.title AS title, q.url AS url 
                                 ORDER BY q.title''', name=field_name).data()

        return questions

    @staticmethod
    def find_subfields(field_name):

        """finds all subfields of a field

            :param field_name: the name of the field
            :returns: a list of dictionaries that represent all subfields of the field"""

        fields = graph.run('''MATCH (f:Field{name:{name}})-[:include]->(f2:Field) 
                              OPTIONAL MATCH (f)-[:include]->(f2)-[:include]->(f3:Field)
                              WITH f2, f3
                              ORDER BY f3.name
                              RETURN f2.name AS name, collect(f3.name) AS subfields, f2.uuid AS uuid
                              ORDER BY f2.name''', name=field_name).data()  # empty list if level 3

        return fields

    @staticmethod
    def find_subfields_2(field_uuid, uuid_classification):

        """finds all subfields of a field

            :param field_name: the name of the field
            :returns: a list of dictionaries that represent all subfields of the field"""

        fields = graph.run('''MATCH (c:Classification{uuid:{uuid_classification}})-[:include*]->(f:Field{uuid:{field_uuid}})-[:include]->(f2:Field) 
                                  OPTIONAL MATCH (f)-[:include]->(f2)-[:include]->(f3:Field)
                                  WITH f2, f3
                                  ORDER BY f3.name
                                  RETURN f2.name AS name, collect(f3.name) AS subfields, f2.uuid AS uuid
                                  ORDER BY f2.name''', field_uuid=field_uuid,
                           uuid_classification=uuid_classification).data()  # empty list if level 3
        return fields

    @staticmethod
    def find_concerned_fields(field_name):

        """finds all fields linked to a field

            :param field_name: the name of the field
            :returns: the names of the fields linked to the desired field"""

        fields = graph.run('''OPTIONAL MATCH (f:Field{name:{name}})-[:concerns]-(f2:Field) 
                              RETURN f2.name AS name, f2.uuid AS uuid
                              ORDER BY f2.name''', name=field_name).data()

        return fields

    @staticmethod
    def find_all_fields():

        """finds all fields of the classification

            :returns: all fields of the classification"""

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

        all_fields = []
        for rootField in levels_1_2:
            root_field_dict = {}
            root_field_dict["name"] = rootField['name']
            root_field_dict["subfields"] = []
            fields_used = []

            for field_L2 in levels_2_3:
                if field_L2["name_L2"] in rootField['subfields']:  # rootField['subfields'] is an str list
                    sub_field_dict = {}
                    sub_field_dict["name"] = field_L2['name_L2']
                    sub_field_dict["subfields"] = []
                    for field_L3 in field_L2['subfields_L3']:
                        if field_L3 not in sub_field_dict["subfields"]:  # to not have 2 x subfields
                            sub_field_dict["subfields"].append(field_L3)  # when one node included by two fields
                    root_field_dict["subfields"].append(sub_field_dict)
                    fields_used.append(field_L2['name_L2'])

            for field_L2_name in rootField['subfields']:  # for levels 2 which don't have a level 3
                if field_L2_name not in fields_used:
                    sub_field_dict = {}
                    sub_field_dict["name"] = field_L2_name
                    sub_field_dict["subfields"] = []
                    root_field_dict["subfields"].append(sub_field_dict)

            all_fields.append(root_field_dict)

        # sorts alphabetically
        for x in all_fields:
            sorted_list_of_dict = sorted(x["subfields"], key=lambda k: k['name'])  # sort a list of dictionaries by the
            # key: name (level 2)
            x["subfields"] = sorted_list_of_dict
            '''for y in x["subfields"]:
                sortedList = sorted(y["subfields"])  #sort simply a list of strings (level 3)
                y["subfields"] = sortedList'''

        return all_fields

    @staticmethod
    def find_classification(uuid):

        """ Find all field of a classification

        :param uuid: the uuid of the concerned classification
        :return: A dictionary that represent the classification desired"""

        req = graph.run('''MATCH (c:Classification{uuid:{uuid}})-[:include]->(f:Field)
                           RETURN f''', uuid=uuid).data()
        if not req:  # so if request empty
            req2 = graph.run('''OPTIONAL MATCH (c:Classification{uuid:{uuid}})-[:forked_from]->(c2:Classification)
                               WHERE EXISTS (c2.uuid)
                               RETURN c2.uuid AS uuid''', uuid=uuid).data()
            uuid = req2[0]['uuid']  # take the uuid of the ancestor classification (case where someone fork a
            # classification and doesn't do modification)

        levels_1_2 = graph.run('''MATCH (c:Classification{uuid:{uuid}})-[:include]->(f:Field{level:1})
                                      -[:include]->(f2:Field) 
                                      WITH f, f2
                                      ORDER BY f2.name
                                      RETURN f.name AS name, collect(f2.name) AS subfields
                                      ORDER BY f.name''', uuid=uuid).data()

        levels_2_3 = graph.run('''MATCH (c:Classification{uuid:{uuid}})-[:include]->(f:Field{level:1})-[:include]->
                                      (f2:Field)-[:include]->(f3:Field)
                                      WITH f2, f3
                                      ORDER BY f3.name
                                      RETURN f2.name AS name_L2, collect(f3.name) AS subfields_L3
                                      ORDER BY f2.name''', uuid=uuid).data()

        all_fields = []
        for rootField in levels_1_2:
            root_field_dict = {}
            root_field_dict["name"] = rootField['name']
            root_field_dict["subfields"] = []
            fields_used = []

            for field_L2 in levels_2_3:
                if field_L2["name_L2"] in rootField['subfields']:  # rootField['subfields'] is an str list
                    sub_field_dict = {}
                    sub_field_dict["name"] = field_L2['name_L2']
                    sub_field_dict["subfields"] = []
                    for field_L3 in field_L2['subfields_L3']:
                        if field_L3 not in sub_field_dict["subfields"]:  # to not have 2 x subfields
                            sub_field_dict["subfields"].append(field_L3)  # when one node included by two fields
                    root_field_dict["subfields"].append(sub_field_dict)
                    fields_used.append(field_L2['name_L2'])

            for field_L2_name in rootField['subfields']:  # for levels 2 which don't have a level 3
                if field_L2_name not in fields_used:
                    sub_field_dict = {}
                    sub_field_dict["name"] = field_L2_name
                    sub_field_dict["subfields"] = []
                    root_field_dict["subfields"].append(sub_field_dict)

            all_fields.append(root_field_dict)

        # sorts alphabetically
        for x in all_fields:
            sorted_list_of_dict = sorted(x["subfields"], key=lambda k: k['name'])  # sort a list of dictionaries by the
            # key: name (level 2)
            x["subfields"] = sorted_list_of_dict
            '''for y in x["subfields"]:
                sortedList = sorted(y["subfields"])  #sort simply a list of strings (level 3)
                y["subfields"] = sortedList'''

        return all_fields

    @staticmethod
    def delete_all():

        """Clears the entire database"""

        graph.run('''MATCH (n)
                     DETACH DELETE n ''')

    @staticmethod
    def fields_creation():

        """Creates the classification into the database"""

        with app.open_resource('db_creation/fields.json') as file:
            fields = json.load(file)['items']

            for field in fields:
                Database.add_field(field['field'], 1)
                for subfield in field['subfields']:
                    Database.add_field(subfield['subfield'], 2)
                    Database.add_subfield_relationship(field['field'], subfield['subfield'])
                    for subsubfield in subfield['subsubfields']:
                        Database.add_field(subsubfield, 3)
                        Database.add_subfield_relationship(subfield['subfield'], subsubfield)

            # because one node is linked to more of one other node
            Database.add_subfield_relationship('services', 'cloud computing')
            Database.add_subfield_relationship('Software', 'DBMS')
            Database.add_subfield_relationship('Computer systems',
                                               'Operating systems')  # car os a plsr champs, comment faire dans arborescence?
            Database.add_subfield_relationship('mobile development', 'Visual Studio')
            Database.add_subfield_relationship('mobile development', 'Unity')
            Database.add_subfield_relationship('Software', 'os types')

    @staticmethod
    def buzz_words_links_creation():

        """Creates buzz words and theirs relationship with the classification into the database"""

        with app.open_resource('db_creation/buzz_words_links.json') as file:
            data = json.load(file)

            for key, value in data.items():
                Database.add_buzz_word(key)
                for field in value:
                    Database.add_is_linked_to_relationship(key, field)

    @staticmethod
    def fields_links_creation():

        """Creates the relationship between fields that are linked to each other"""

        with app.open_resource('db_creation/fields_links.json') as file:
            data = json.load(file)

            for key, value in data.items():
                for field in value:
                    Database.add_concerns_relationship(key, field)

    @staticmethod
    def classification_creation():
        """Creation of the cs-classify classification """

        with app.open_resource('db_creation/classification.json') as file:
            data = json.load(file)

            for key, value in data.items():
                classification_uuid = Database.add_classification(key)  # add checking if don't exist
                Database.add_subclassification_relationship(classification_uuid, value)

    @staticmethod
    def database_creation():

        """Create the entire Neo4j Editx Database"""

        Database.fields_creation()
        Database.buzz_words_links_creation()
        Database.fields_links_creation()
        Database.classification_creation()

    @staticmethod
    def mongodb_creation():

        """Create the entire MongoDB cs-classify Database"""

        classification = {
            'name': 'cs-classify',
            'is_forked': False,
            'details': 'blabla présentation',
            'user_id': 123,
            'logs': [
                {'timestamp': 1,
                 'request': 'MATCH(n:Classification) RETURN n'}
            ]
        }

        users = {
            'firstname': 'Houda',
            'lastname': 'Hannouni',
            'job': 'student',
            'website': 'www.cs-classify.net',
            'pseudo': 'Miss H',
            'password': 'Blabla'
        }

        db.Classification.insert_one(classification)  # Collection : Classification
        db.Users.insert_one(users)  # Collection : Users
