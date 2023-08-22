from autosar_data import *
import pytest

def test_element_basic():
    model = AutosarModel()

    # create some elements
    el_ar_packages = model.root_element.create_sub_element(specification.ElementName.ArPackages)
    el_ar_package = el_ar_packages.create_named_sub_element(specification.ElementName.ArPackage, "Pkg1")
    assert isinstance(el_ar_packages, Element)
    assert isinstance(el_ar_package, Element)

    # each element has a parent, only the root_element does not
    assert el_ar_package.parent == el_ar_packages
    assert model.root_element.parent is None

    # each element is part of the model
    assert el_ar_packages.model == model
    assert el_ar_package.model == model

    # identifiable elements always have a ShortName sub element
    assert el_ar_package.is_identifiable
    el_short_name = el_ar_package.get_sub_element(specification.ElementName.ShortName)
    assert isinstance(el_short_name, Element)

    # properties of named elements
    assert el_ar_package.item_name == "Pkg1"
    assert el_ar_package.path == "/Pkg1"

    # the name can be changed
    el_ar_package.item_name = "NewName"
    assert el_ar_package.item_name == "NewName"
    assert el_ar_package.path == "/NewName"

    # these properies are not valid for elements that are not identifiable
    assert el_ar_packages.is_identifiable == False
    assert el_ar_packages.item_name is None
    with pytest.raises(AutosarDataError):
        print(el_ar_packages.path)
    
    # the behavior of the element is determined by its element_type
    assert el_ar_packages.is_identifiable == el_ar_packages.element_type.is_named
    assert el_ar_packages.is_reference == el_ar_packages.element_type.is_ref
    assert not el_ar_packages.element_type.is_ordered
    assert el_ar_packages.element_type.splittable != 0
    
    # Element has __str__ and __repr__
    el_ar_packages_repr = el_ar_packages.__repr__()
    assert not el_ar_packages_repr is None
    el_ar_packages_str = el_ar_packages.__str__()
    assert not el_ar_packages_str is None
    assert el_ar_packages_repr != el_ar_packages_str

    # elements can be serialized
    el_ar_packages_text = el_ar_packages.serialize()
    # this is currently the same as __str__()
    assert el_ar_packages_text == el_ar_packages_str

    # Element has __hash__
    elementset = set([el_ar_packages, el_ar_package])
    assert len(elementset) == 2

    # Element comparison
    assert model.get_element_by_path("/NewName") == el_ar_package
    assert el_ar_packages != el_ar_package

    # Elements can be sorted
    el_ar_packages.create_named_sub_element(specification.ElementName.ArPackage, "AAA")
    sub_elements = [e for e in el_ar_packages.sub_elements]
    assert sub_elements[0].item_name == "NewName"
    assert sub_elements[1].item_name == "AAA"
    # sort all sub elements recursively
    el_ar_packages.sort()
    sub_elements = [e for e in el_ar_packages.sub_elements]
    assert sub_elements[0].item_name == "AAA"
    assert sub_elements[1].item_name == "NewName"

    # every alement has an "xml path" this path includes the names and item names of all parent elements
    assert el_ar_package.xml_path == "/<AUTOSAR>/<AR-PACKAGES>/NewName"


def test_element_content():
    model = AutosarModel()

    # create some elements for the test
    el_ar_packages = model.root_element.create_sub_element(specification.ElementName.ArPackages)
    el_pkg1 = el_ar_packages.create_named_sub_element(specification.ElementName.ArPackage, "Pkg1")
    el_short_name = el_pkg1.get_sub_element(specification.ElementName.ShortName)
    el_l2 = el_pkg1 \
        .create_sub_element(specification.ElementName.Desc) \
        .create_sub_element(specification.ElementName.L2)
    
    # different elements have different content types
    assert el_pkg1.content_type == ContentType.Elements
    assert el_short_name.content_type == ContentType.CharacterData
    assert el_l2.content_type == ContentType.Mixed

    # create some items for the content of el_l2
    el_l2.insert_character_content_item("text", 0)
    assert len([c for c in el_l2.content]) == 1
    el_l2.create_sub_element(specification.ElementName.Br)
    assert len([c for c in el_l2.content]) == 2

    # check the content
    content = [c for c in el_l2.content]
    assert isinstance(content[0], str)
    assert isinstance(content[1], Element)

    # remove an item
    el_l2.remove_character_content_item(0)
    assert len([c for c in el_l2.content]) == 1

    # *_character_content_item is not valid for elements with ContentType.CharacterData
    with pytest.raises(AutosarDataError):
        el_short_name.insert_character_content_item("text", 0)

    el_elements = el_ar_packages \
        .create_named_sub_element(specification.ElementName.ArPackage, "SysPkg") \
        .create_sub_element(specification.ElementName.Elements)
    el_fibex_element_ref = el_elements \
        .create_named_sub_element(specification.ElementName.System, "System") \
        .create_sub_element(specification.ElementName.FibexElements) \
        .create_sub_element(specification.ElementName.FibexElementRefConditional) \
        .create_sub_element(specification.ElementName.FibexElementRef)
    el_can_cluster = model.root_element \
        .get_sub_element(specification.ElementName.ArPackages) \
        .create_named_sub_element(specification.ElementName.ArPackage, "CanPkg") \
        .create_sub_element(specification.ElementName.Elements) \
        .create_named_sub_element(specification.ElementName.CanCluster, "CanCluster")
    
    # various character data elements have constraints, e.g the reference element can only contain an autosar path
    # integers, or strings that do not look like paths cause an exception
    with pytest.raises(AutosarDataError):
        el_fibex_element_ref.character_data = 1
    with pytest.raises(AutosarDataError):
        el_fibex_element_ref.character_data = "? what ?"
    # "looks like" an autosar path
    el_fibex_element_ref.character_data = "/something/else"

    # there is special handling for references
    with pytest.raises(AutosarDataError):
        invalid = el_fibex_element_ref.reference_target
    # set the reference to a valid element
    el_fibex_element_ref.reference_target = el_can_cluster
    assert el_fibex_element_ref.character_data == "/CanPkg/CanCluster"

    # remove the character data
    el_fibex_element_ref.remove_character_data()
    assert el_fibex_element_ref.character_data is None


def test_element_creation():
    model = AutosarModel()

    # create an unnamed element
    el_ar_packages = model.root_element.create_sub_element(specification.ElementName.ArPackages)

    # create a named element
    el_pkg1 = el_ar_packages.create_named_sub_element(specification.ElementName.ArPackage, "Pkg1")

    # create an element at a given position
    # not every position is allowed
    with pytest.raises(AutosarDataError):
        el_elements = el_pkg1.create_sub_element_at(specification.ElementName.Elements, 0)
    # position 1 (after ShortName) is allowed
    assert len([e for e in el_pkg1.sub_elements]) == 1
    el_elements = el_pkg1.create_sub_element_at(specification.ElementName.Elements, 1)

    # create a named sub element at a given position
    el_elements.create_named_sub_element_at(specification.ElementName.System, "System", 0)

    # create an element by copying another element and all of its sub elements
    el_pkg2 = el_ar_packages.create_copied_sub_element(el_pkg1)
    # because the item_name must be unique among the siblings, the element might be renamed while copying
    assert el_pkg2.item_name == "Pkg1_1"
    el_pkg2.item_name = "Pkg2"
    copied_system = el_pkg2.get_sub_element(specification.ElementName.Elements).get_sub_element(specification.ElementName.System)
    assert copied_system.item_name == "System"
    assert copied_system.path == "/Pkg2/System"

    # create a copied elelemt at a given position
    el_pkg3 = el_ar_packages.create_copied_sub_element_at(el_pkg1, 0)
    el_pkg3.item_name = "Pkg3"

    # elements can be moved to a different parent, as long as this results in a valid hierarchy
    # not valid: ArPackage inside Arpackage
    with pytest.raises(AutosarDataError):
        el_pkg1.move_element_here(el_pkg2)
    # valid: ArPackage inside Arpackages
    el_pkg1.create_sub_element(specification.ElementName.ArPackages).move_element_here(el_pkg2)
    assert el_pkg2.path == "/Pkg1/Pkg2"
    assert copied_system.path == "/Pkg1/Pkg2/System"

    # move_element_here_at can move elements to a specified position within a target element
    # it can also be used to re-oder elements inside the current element
    sub_elements = [e for e in el_ar_packages.sub_elements]
    assert sub_elements[0] == el_pkg3
    assert sub_elements[1] == el_pkg1
    el_ar_packages.move_element_here_at(el_pkg3, 1)
    sub_elements = [e for e in el_ar_packages.sub_elements]
    assert sub_elements[0] == el_pkg1
    assert sub_elements[1] == el_pkg3

    # in all cases only valid sub elements can be created
    # el_pkg1 already has a ShortName, and only one of these is allowed
    with pytest.raises(AutosarDataError):
        el_pkg1.create_sub_element(specification.ElementName.ShortName)
    # the element Autosar is not a valid sub element of ArPackage
    with pytest.raises(AutosarDataError):
         el_pkg1.create_sub_element_at(specification.ElementName.Autosar, 1)
    
    # it is possible to check which sub elements would be valid
    # returns a list of tuples: (ElementName, is_named, currently_allowed)
    allowed_elements = [ename if allowed else None for (ename, identifiable, allowed) in el_pkg1.list_valid_sub_elements()]
    assert not specification.ElementName.Autosar in allowed_elements
    assert specification.ElementName.Category in allowed_elements
    
    # remove an element
    el_ar_packages.remove_sub_element(el_pkg3)
    with pytest.raises(AutosarDataError):
        invalid = el_pkg3.path
    with pytest.raises(AutosarDataError):
        invalid = el_pkg3.model
    
    # validate the resulting model
    element_info = [x for x in model.root_element.elements_dfs]
    # element info is a list of tuple(depth, element)
    assert element_info[0][1].element_name == specification.ElementName.Autosar
    assert element_info[1][1].element_name == specification.ElementName.ArPackages
    assert element_info[2][1].element_name == specification.ElementName.ArPackage
    assert element_info[2][1].item_name == "Pkg1"
    assert element_info[3][1].element_name == specification.ElementName.ShortName
    assert element_info[4][1].element_name == specification.ElementName.Elements
    assert element_info[5][1].element_name == specification.ElementName.System
    assert element_info[5][1].item_name == "System"
    assert element_info[6][1].element_name == specification.ElementName.ShortName
    assert element_info[7][1].element_name == specification.ElementName.ArPackages
    assert element_info[8][1].element_name == specification.ElementName.ArPackage
    assert element_info[8][1].item_name == "Pkg2"
    assert element_info[9][1].element_name == specification.ElementName.ShortName
    assert element_info[10][1].element_name == specification.ElementName.Elements
    assert element_info[11][1].element_name == specification.ElementName.System
    assert element_info[11][1].item_name == "System"
    assert element_info[12][1].element_name == specification.ElementName.ShortName
    assert len(element_info) == 13
    
def test_element_attributes():
    model = AutosarModel()
    el_autosar = model.root_element

    attributes = [attr for attr in el_autosar.attributes]
    assert isinstance(attributes[0], Attribute)
    assert attributes[0].attrname == specification.AttributeName.xsiSchemalocation
    assert attributes[1].attrname == specification.AttributeName.xmlns
    assert attributes[1].content == "http://autosar.org/schema/r4.0"
    assert attributes[2].attrname == specification.AttributeName.xmlnsXsi
    assert attributes[2].content == "http://www.w3.org/2001/XMLSchema-instance"
    assert len(attributes) == 3

    # __repr__ and __str__ exist for Attribute
    assert not attributes[0].__repr__() is None
    assert not attributes[0].__str__() is None

    el_autosar.set_attribute(specification.AttributeName.S, "some text")
    # attribute values are checked - attribute T must contain a valid timestamp
    with pytest.raises(AutosarDataError):
        el_autosar.set_attribute(specification.AttributeName.T, "some text")
    # the function set_attribute_string automatically converts an input string to enum or integer if the attribute requires this
    el_autosar.set_attribute_string(specification.AttributeName.T, "2023-04-05T12:34:56Z")
    assert el_autosar.attribute_value(specification.AttributeName.T) == "2023-04-05T12:34:56Z"

    assert len([attr for attr in el_autosar.attributes]) == 5
    el_autosar.remove_attribute(specification.AttributeName.T)
    assert len([attr for attr in el_autosar.attributes]) == 4


def test_file_membership():
    model = AutosarModel()
    file1 = model.create_file("file1", specification.AutosarVersion.Autosar_00050)
    file2 = model.create_file("file2", specification.AutosarVersion.Autosar_00050)
    el_ar_packages = model.root_element.create_sub_element(specification.ElementName.ArPackages)
    el_pkg1 = el_ar_packages.create_named_sub_element(specification.ElementName.ArPackage, "Pkg1")
    el_pkg1.create_sub_element(specification.ElementName.Elements)
    el_pkg2 = el_ar_packages.create_named_sub_element(specification.ElementName.ArPackage, "Pkg2")

    total_element_count = len([e for e in model.elements_dfs])
    # initially all elements are part of every file
    file1_element_count = len([e for e in file1.elements_dfs])
    assert total_element_count == file1_element_count
    assert file1 in el_pkg1.file_membership[1]
    assert file2 in el_pkg1.file_membership[1]

    # remove pkg1 from file2 and pkg2 from file1
    el_pkg1.remove_from_file(file2)
    el_pkg2.remove_from_file(file1)
    file1_element_count = len([e for e in file1.elements_dfs])
    file2_element_count = len([e for e in file2.elements_dfs])
    assert file1_element_count < total_element_count
    assert file2_element_count < total_element_count
    assert file1_element_count != file2_element_count

    # directly copy the file membership from el_pkg1 to el_pkg2
    el_pkg2.file_membership = el_pkg1.file_membership
    assert len(el_pkg2.file_membership[1]) == 1
    assert file1 in el_pkg2.file_membership[1]

    # add el_pkg2 to file2 again and remove it from file1
    el_pkg2.add_to_file(file2)
    el_pkg2.remove_from_file(file1)
    assert len(el_pkg2.file_membership[1]) == 1
    assert file2 in el_pkg2.file_membership[1]