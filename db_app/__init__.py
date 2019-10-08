from .views import app
from .models import graph

'''creating constraint for labels to not have any duplicate node '''

def create_uniqueness_constraint(label, property):
    query = "CREATE CONSTRAINT ON (n:{label}) ASSERT n.{property} IS UNIQUE"
    query = query.format(label=label, property=property)
    graph.cypher.execute(query)

create_uniqueness_constraint("Root_field", "name")
create_uniqueness_constraint("Subfield", "name")
create_uniqueness_constraint("Question", "title")