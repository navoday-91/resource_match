# Resource To Group Matching Algorithm:

## Requirements:
- pandas

## Installation:
```pip install pandas```
or
```pip install requirements.txt```

## Execution:
```
git clone https://github.com/navoday-91/resource_match.git
python application.py
```
Follow the instructions on prompt:

- **You want to include rules with inequality(<,>)? Y/N:**
  Enter 'Y' or 'y' if your rules are having  inequality conditions(< or >) and you want to match against them. e.g. group with rule age > 15 should match for all entities with age = n where n>15.
- **Please provide the path to file with Entity Group Rules:**
  Provide the path to csv file containing group rule definitions. See group_rules.csv for format.
- **How do you want to feed query entities? (F)ile or (I)nput via Keyboard?:**
  You can provide a csv file with entity definitions or input entity definition via keyboard input. Refer entities.csv for format. Follow the formatting instructions for Keyboard Input as well. "()" is optional for entity definitions.
- **How do you want to match? (B)lanket match for missing attributes or S(trict) match?**
#### Blanket Match:
  Any missing attribute on the entity will be considered as "*" or ALL value hence matching to any group rule having that attribute. Only if the attribute is present with a specific value on the entity, it will not be a match to a group rule for that attribute with different value. Entity(gender=M) will be a match into an Entity Group(gender=M;nationality=US). Entity() will be considered as a super group matching to all entity groups.

#### Strict Match:
  Groups will be matched to an entity only when all the rules for that group are satisfied by the entity strictly. Missing attributes won't be considered a match. e.g. Entity(gender=M) will not match into an Entity Group(gender=M;nationality=US)

### Sample Input/Output for File Input for Query Data:
```
Please provide the path to file with Entity Group Rules: 
group_rules.csv
Indexing your data......
Complete!

How do you want to feed query entities? (F)ile or (I)nput via Keyboard?
F
Please enter the path to file containing entities for search:
entities.csv
How do you want to match? (B)lanket match for missing attributes or S(trict) match?
B
E1 -> (gender=M;nationality=India;education=MS;age=30) -> {'EG4', 'EG5', 'EG2', 'EG3'}
E2 -> (engine=3000cc) -> {'EG4', 'EG2', 'EG3', 'EG5', 'EG1'}
E3 -> (engine=3000cc;drive=2W) -> {'EG2', 'EG4', 'EG3', 'EG1'}
E4 -> () -> {'EG3', 'EG1', 'EG2', 'EG5', 'EG4'}
E5 -> (gender=F;nationality=US) -> {'EG5', 'EG1'}
E6 -> (gender=M;education=MS) -> {'EG4', 'EG5', 'EG2', 'EG3'}
E7 -> (nationality=India;education=MS) -> {'EG4', 'EG5', 'EG2', 'EG3'}
E8 -> (nationality=US) -> {'EG4', 'EG5', 'EG1'}
```
**Note:** All data structures for rule storage use hashing(Python Dict and Sets) hence yielding a time complexity of O(1) for querying/accessing/storing any data.

