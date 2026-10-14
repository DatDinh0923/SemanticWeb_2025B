"""Bao đóng RDFS bằng forward chaining (luật rdfs1–rdfs13 của RDF 1.1 Semantics + vài axiomatic triple)
rồi kiểm tra 18 mệnh đề của Part 2 – Ex2: TRUE nếu được suy ra, UNKNOWN nếu không.

Dùng:  python rdfs_closure.py
Mệnh đề có blank node được kiểm tra bằng ASK (blank node trong pattern = biến tồn tại, đúng ý nghĩa se2).
"""
from pathlib import Path

from rdflib import Graph, Literal, RDF, RDFS

HERE = Path(__file__).parent

# Một phần axiomatic triples của RDFS (đủ cho các mệnh đề trong bài)
AXIOMS = """
@prefix rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
rdf:type           rdfs:domain rdfs:Resource ; rdfs:range rdfs:Class .
rdfs:domain        rdfs:domain rdf:Property  ; rdfs:range rdfs:Class .
rdfs:range         rdfs:domain rdf:Property  ; rdfs:range rdfs:Class .
rdfs:subPropertyOf rdfs:domain rdf:Property  ; rdfs:range rdf:Property .
rdfs:subClassOf    rdfs:domain rdfs:Class    ; rdfs:range rdfs:Class .
rdf:subject   rdfs:domain rdf:Statement .
rdf:predicate rdfs:domain rdf:Statement .
rdf:object    rdfs:domain rdf:Statement .
"""


def closure(g):
    """Áp dụng lặp các luật cho tới điểm bất động (không sinh tài nguyên mới)."""
    while True:
        new = set()
        for s, p, o in g:
            new.add((s, RDF.type, RDFS.Resource))                      # rdfs4a
            if not isinstance(o, Literal):
                new.add((o, RDF.type, RDFS.Resource))                  # rdfs4b
            new.add((p, RDF.type, RDF.Property))                       # rdf1
            for c in g.objects(p, RDFS.domain):
                new.add((s, RDF.type, c))                              # rdfs2
            if not isinstance(o, Literal):
                for c in g.objects(p, RDFS.range):
                    new.add((o, RDF.type, c))                          # rdfs3
            for q in g.objects(p, RDFS.subPropertyOf):
                new.add((s, q, o))                                     # rdfs7
        for c in g.subjects(RDF.type, RDFS.Class):
            new.add((c, RDFS.subClassOf, RDFS.Resource))               # rdfs8
            new.add((c, RDFS.subClassOf, c))                           # rdfs10
        for p in g.subjects(RDF.type, RDF.Property):
            new.add((p, RDFS.subPropertyOf, p))                        # rdfs6
        for c, d in g.subject_objects(RDFS.subClassOf):
            for x in g.subjects(RDF.type, c):
                new.add((x, RDF.type, d))                              # rdfs9
            for e in g.objects(d, RDFS.subClassOf):
                new.add((c, RDFS.subClassOf, e))                       # rdfs11
        for p, q in g.subject_objects(RDFS.subPropertyOf):
            for r in g.objects(q, RDFS.subPropertyOf):
                new.add((p, RDFS.subPropertyOf, r))                    # rdfs5
        for p in g.subjects(RDF.type, RDFS.ContainerMembershipProperty):
            new.add((p, RDFS.subPropertyOf, RDFS.member))              # rdfs12
        for c in g.subjects(RDF.type, RDFS.Datatype):
            new.add((c, RDFS.subClassOf, RDFS.Literal))                # rdfs13
        before = len(g)
        for t in new:
            g.add(t)
        if len(g) == before:
            return g


BASE = """
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix : <http://example.com/terms#> .
:Person a rdfs:Class .
:Man a rdfs:Class ; rdfs:subClassOf :Person .
:Parent a rdfs:Class ; rdfs:subClassOf :Person .
:Father a rdfs:Class ; rdfs:subClassOf :Parent ; rdfs:subClassOf :Man .
:Child a rdfs:Class ; rdfs:subClassOf :Person .
:hasParent a rdf:Property ; rdfs:domain :Person ; rdfs:range :Parent .
:hasFather a rdf:Property ; rdfs:subPropertyOf :hasParent ; rdfs:range :Father .
:isChildOf a rdf:Property ; rdfs:domain :Child ; rdfs:range :Parent .
:Ann a :Person ; :hasFather :Carl .
:Carl a :Man .
"""

STATEMENTS = [
    ":Father rdfs:subClassOf :Person .",
    ":Man rdfs:subClassOf :Person .",
    ":Carl a :Person .",
    ":Carl a :Parent .",
    ":Carl :hasChild :Ann .",
    ":Carl a :Man .",
    ":Carl a :Father .",
    ":Child rdf:type rdfs:Resource .",
    ":Ann a :Child .",
    ":Ann :isChildOf :Carl .",
    ":Ann :hasParent :Carl .",
    ":Ann :hasParent _:x .",
    ":Ann :hasParent [ rdf:type :Person ] .",
    ":hasFather rdfs:domain :Person .",
    "rdfs:range rdf:type rdfs:Resource .",
    ":hasFather rdfs:range :Father .",
    ":hasFather rdfs:domain [ rdfs:subClassOf :Person ] .",
    ":Father rdfs:subClassOf [ rdfs:subClassOf :Person ] .",
]

PREFIXES = """PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX : <http://example.com/terms#>
"""

if __name__ == "__main__":
    g = Graph()
    g.parse(data=AXIOMS, format="turtle")
    g.parse(data=BASE, format="turtle")
    n0 = len(g)
    closure(g)
    print(f"Bao đóng: {n0} -> {len(g)} triple\n")
    for i, st in enumerate(STATEMENTS, 1):
        ok = g.query(PREFIXES + "ASK { " + st + " }").askAnswer
        print(f"{i:2}. {st:55} {'TRUE' if ok else 'UNKNOWN'}")
