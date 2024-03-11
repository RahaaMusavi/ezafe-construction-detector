from conllu import parse
from prettytable import PrettyTable
import os
import pandas as pd

#creating the class for tokens
class Token:
    def __init__(self, id_, form, lemma, upos, xpos, feats, head, deprel, deps, misc):
        self.id = id_
        self.form = form
        self.lemma = lemma
        self.upos = upos
        self.xpos = xpos
        self.feats = feats
        self.head = head
        self.deprel = deprel
        self.deps = deps
        self.misc = misc

    def __str__(self):
        return f"Token(id={self.id}, form={self.form}, lemma={self.lemma}, " \
               f"upos={self.upos}, xpos={self.xpos}, feats={self.feats}, " \
               f"head={self.head}, deprel={self.deprel}, deps={self.deps}, misc={self.misc})"

# reading from a CoNLL-U file and create Token objects
def read_conllu_file(file_path):
    token_list = []
    with open(file_path, 'r', encoding='utf-8') as data_file:
        data = data_file.read()
        sentences = parse(data)

        for sentence in sentences:
            for token_data in sentence:
                token = Token(
                    id_=token_data['id'],
                    form=token_data['form'],
                    lemma=token_data['lemma'],
                    upos=token_data['upos'],
                    xpos=token_data['xpos'],
                    feats=token_data['feats'],
                    head=token_data['head'],
                    deprel=token_data['deprel'],
                    deps=token_data['deps'],
                    misc=token_data['misc']
                )
                token_list.append(token)
    return token_list

# Function for finding ezafe constructions in the list of Token objects
def find_ezafe_constructions(token_list):
    constr_list = []
    for token in token_list:
        if token.lemma == 'ī':
            ez_head = token.head
            first_attr = None
            for t in token_list:
                if t.id == ez_head:
                    first_attr = t
                    break

            if first_attr:
                other_attrs = [t for t in token_list if t.head == first_attr.head]

                constr_head = None
                for t in token_list:
                    if t.id == first_attr.head:
                        constr_head = t
                        break

                if constr_head:
                    # children are those whose heads match the ID of constr_head
                    constr_children = [t for t in token_list if t.head == constr_head.id]
                    constr = (constr_head, token, first_attr, other_attrs, constr_children)
                    constr_list.append(constr)
    return constr_list

# Main function to process all files in a folder
def process_folder(folder_path):
    all_constructions = []
    for filename in os.listdir(folder_path):
        if filename.endswith(".conllu"):
            file_path = os.path.join(folder_path, filename)
            token_list = read_conllu_file(file_path)
            constructions = find_ezafe_constructions(token_list)
            all_constructions.extend(constructions)
    return all_constructions

# Main function to handle the processing
def main():
    folder_path = 'D:\\ddd\RUB\\nominal flexion\\Forschungsproject'
    all_constructions = process_folder(folder_path)

    # Creating a DataFrame to save all ezafe constructions
    columns = ["Construction Head", "Ezafe", "First Attribute", "Other Attributes", "Children"]
    data = []
    for constr in all_constructions:
        other_attr_forms = [attr.form for attr in constr[3]]
        children_forms = [child.form for child in constr[4]]
        data.append([constr[0].form, constr[1].form, constr[2].form, ', '.join(other_attr_forms), ', '.join(children_forms)])

    df = pd.DataFrame(data, columns=columns)

    # Dumping all ezafe constructions to an output file
    output_file = 'ezafe_constructions_output.csv'
    df.to_csv(output_file, index=False)

    # Creating a pretty table for visualization
    constr_table = PrettyTable()
    constr_table.field_names = columns
    for row in data:
        constr_table.add_row(row)
    print(constr_table)

if __name__ == "__main__":
    main()
