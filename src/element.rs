use std::collections::hash_map::DefaultHasher;
use std::collections::HashSet;
use std::hash::Hash;
use std::hash::Hasher;

use crate::*;
use ::autosar_data as autosar_data_rs;
use pyo3::exceptions::PyTypeError;

#[pymethods]
impl Element {
    fn __repr__(&self) -> String {
        format!("{:#?}", self.0)
    }

    fn __str__(&self) -> String {
        self.0.serialize()
    }

    fn __richcmp__(&self, other: &Element, op: pyo3::basic::CompareOp) -> bool {
        match op {
            pyo3::pyclass::CompareOp::Eq => self.0 == other.0,
            pyo3::pyclass::CompareOp::Ne => self.0 != other.0,
            pyo3::pyclass::CompareOp::Lt
            | pyo3::pyclass::CompareOp::Le
            | pyo3::pyclass::CompareOp::Gt
            | pyo3::pyclass::CompareOp::Ge => false,
        }
    }

    fn __hash__(&self) -> isize {
        let mut hasher = DefaultHasher::new();
        self.0.hash(&mut hasher);
        hasher.finish() as isize
    }

    fn serialize(&self) -> String {
        self.0.serialize()
    }

    #[getter]
    fn parent(&self) -> PyResult<Option<Element>> {
        match self.0.parent() {
            Ok(Some(parent)) => Ok(Some(Element(parent))),
            Ok(None) => Ok(None),
            Err(error) => Err(AutosarDataError::new_err(error.to_string())),
        }
    }

    #[getter]
    fn element_name(&self) -> autosar_data_rs::ElementName {
        self.0.element_name()
    }

    #[getter]
    fn element_type(&self) -> ElementType {
        ElementType(self.0.element_type())
    }

    #[getter]
    fn item_name(&self) -> Option<String> {
        self.0.item_name()
    }

    #[setter]
    fn set_item_name(&self, new_name: &str) -> PyResult<()> {
        match self.0.set_item_name(new_name) {
            Ok(()) => Ok(()),
            Err(error) => Err(AutosarDataError::new_err(error.to_string())),
        }
    }

    #[getter]
    fn is_identifiable(&self) -> bool {
        self.0.is_identifiable()
    }

    #[getter]
    fn is_reference(&self) -> bool {
        self.0.element_type().is_ref()
    }

    #[getter]
    fn path(&self) -> PyResult<String> {
        match self.0.path() {
            Ok(path) => Ok(path),
            Err(error) => Err(AutosarDataError::new_err(error.to_string())),
        }
    }

    #[getter]
    fn model(&self) -> PyResult<AutosarModel> {
        match self.0.model() {
            Ok(model) => Ok(AutosarModel(model)),
            Err(error) => Err(AutosarDataError::new_err(error.to_string())),
        }
    }

    #[getter]
    fn content_type(&self) -> ContentType {
        match self.0.content_type() {
            autosar_data_rs::ContentType::Elements => ContentType::Elements,
            autosar_data_rs::ContentType::CharacterData => ContentType::CharacterData,
            autosar_data_rs::ContentType::Mixed => ContentType::Mixed,
        }
    }

    fn create_sub_element(&self, element_name: autosar_data_rs::ElementName) -> PyResult<Element> {
        match self.0.create_sub_element(element_name) {
            Ok(element) => Ok(Element(element)),
            Err(error) => Err(AutosarDataError::new_err(error.to_string())),
        }
    }

    fn create_sub_element_at(
        &self,
        element_name: autosar_data_rs::ElementName,
        position: usize,
    ) -> PyResult<Element> {
        match self.0.create_sub_element_at(element_name, position) {
            Ok(element) => Ok(Element(element)),
            Err(error) => Err(AutosarDataError::new_err(error.to_string())),
        }
    }

    fn create_named_sub_element(
        &self,
        element_name: autosar_data_rs::ElementName,
        item_name: &str,
    ) -> PyResult<Element> {
        match self.0.create_named_sub_element(element_name, item_name) {
            Ok(element) => Ok(Element(element)),
            Err(error) => Err(AutosarDataError::new_err(error.to_string())),
        }
    }

    fn create_named_sub_element_at(
        &self,
        element_name: autosar_data_rs::ElementName,
        item_name: &str,
        position: usize,
    ) -> PyResult<Element> {
        match self
            .0
            .create_named_sub_element_at(element_name, item_name, position)
        {
            Ok(element) => Ok(Element(element)),
            Err(error) => Err(AutosarDataError::new_err(error.to_string())),
        }
    }

    fn create_copied_sub_element(&self, other: &Element) -> PyResult<Element> {
        match self.0.create_copied_sub_element(&other.0) {
            Ok(element) => Ok(Element(element)),
            Err(error) => Err(AutosarDataError::new_err(error.to_string())),
        }
    }

    fn create_copied_sub_element_at(&self, other: &Element, position: usize) -> PyResult<Element> {
        match self.0.create_copied_sub_element_at(&other.0, position) {
            Ok(element) => Ok(Element(element)),
            Err(error) => Err(AutosarDataError::new_err(error.to_string())),
        }
    }

    fn move_element_here(&self, move_element: &Element) -> PyResult<Element> {
        match self.0.move_element_here(&move_element.0) {
            Ok(element) => Ok(Element(element)),
            Err(error) => Err(AutosarDataError::new_err(error.to_string())),
        }
    }

    fn move_element_here_at(&self, move_element: &Element, position: usize) -> PyResult<Element> {
        match self.0.move_element_here_at(&move_element.0, position) {
            Ok(element) => Ok(Element(element)),
            Err(error) => Err(AutosarDataError::new_err(error.to_string())),
        }
    }

    fn remove_sub_element(&self, sub_element: Element) -> PyResult<()> {
        self.0
            .remove_sub_element(sub_element.0)
            .map_err(|error| AutosarDataError::new_err(error.to_string()))
    }

    #[setter]
    fn set_reference_target(&self, target: Element) -> PyResult<()> {
        self.0
            .set_reference_target(&target.0)
            .map_err(|error| AutosarDataError::new_err(error.to_string()))
    }

    #[getter]
    fn get_reference_target(&self) -> PyResult<Element> {
        match self.0.get_reference_target() {
            Ok(target) => Ok(Element(target)),
            Err(error) => Err(AutosarDataError::new_err(error.to_string())),
        }
    }

    fn get_sub_element(&self, name: autosar_data_rs::ElementName) -> Option<Element> {
        self.0.get_sub_element(name).map(Element)
    }

    #[getter]
    fn sub_elements(&self) -> ElementsIterator {
        ElementsIterator(self.0.sub_elements())
    }

    #[getter]
    fn elements_dfs(&self) -> ElementsDfsIterator {
        ElementsDfsIterator(self.0.elements_dfs())
    }

    #[setter]
    fn set_character_data(&self, chardata: PyObject) -> PyResult<()> {
        let cdata = extract_character_data(chardata)?;
        self.0
            .set_character_data(cdata)
            .map_err(|error| AutosarDataError::new_err(error.to_string()))
    }

    fn remove_character_data(&self) -> PyResult<()> {
        self.0
            .remove_character_data()
            .map_err(|error| AutosarDataError::new_err(error.to_string()))
    }

    #[getter]
    fn character_data(&self) -> Option<PyObject> {
        self.0
            .character_data()
            .map(|cdata| character_data_to_object(&cdata))
    }

    fn insert_character_content_item(&self, chardata: &str, position: usize) -> PyResult<()> {
        self.0
            .insert_character_content_item(chardata, position)
            .map_err(|error| AutosarDataError::new_err(error.to_string()))
    }

    fn remove_character_content_item(&self, position: usize) -> PyResult<()> {
        match self.0.remove_character_content_item(position) {
            Ok(()) => Ok(()),
            Err(error) => Err(AutosarDataError::new_err(error.to_string())),
        }
    }

    #[getter]
    fn content(&self) -> ElementContentIterator {
        ElementContentIterator(self.0.content())
    }

    #[getter]
    fn attributes(&self) -> AttributeIterator {
        AttributeIterator(self.0.attributes())
    }

    fn attribute_value(&self, attrname: autosar_data_rs::AttributeName) -> Option<PyObject> {
        Some(character_data_to_object(&self.0.attribute_value(attrname)?))
    }

    fn set_attribute(
        &self,
        attrname: autosar_data_rs::AttributeName,
        value: PyObject,
    ) -> PyResult<()> {
        let cdata = extract_character_data(value)?;
        self.0
            .set_attribute(attrname, cdata)
            .map_err(|error| AutosarDataError::new_err(error.to_string()))
    }

    fn set_attribute_string(
        &self,
        attrname: autosar_data_rs::AttributeName,
        text: &str,
    ) -> PyResult<()> {
        self.0
            .set_attribute_string(attrname, text)
            .map_err(|error| AutosarDataError::new_err(error.to_string()))
    }

    fn remove_attribute(&self, attrname: autosar_data_rs::AttributeName) -> bool {
        self.0.remove_attribute(attrname)
    }

    fn sort(&self) {
        self.0.sort()
    }

    fn list_valid_sub_elements(&self) -> Vec<(autosar_data_rs::ElementName, bool, bool)> {
        self.0.list_valid_sub_elements()
    }

    #[getter]
    fn file_membership(&self) -> PyResult<PyObject> {
        Python::with_gil(|py| match self.0.file_membership() {
            Ok((local, weak_file_set)) => {
                let file_set: Vec<PyObject> = weak_file_set
                    .iter()
                    .filter_map(|weak| {
                        weak.upgrade()
                            .map(|raw| Py::new(py, ArxmlFile(raw)).unwrap().into_py(py))
                    })
                    .collect();
                let frozenset: &PyFrozenSet = PyFrozenSet::new(py, file_set.iter()).unwrap();
                let pytuple: &PyTuple =
                    PyTuple::new(py, [local.to_object(py), frozenset.to_object(py)].iter());
                Ok(pytuple.to_object(py))
            }
            Err(error) => Err(AutosarDataError::new_err(error.to_string())),
        })
    }

    #[setter]
    fn set_file_membership(&self, file_membership_obj: PyObject) -> PyResult<()> {
        Python::with_gil(|py| -> PyResult<()> {
            let iter: Box<dyn Iterator<Item = &PyAny>> = if let Ok(set) =
                file_membership_obj.extract::<&PySet>(py)
            {
                Box::new(set.iter())
            } else if let Ok(frozenset) = file_membership_obj.extract::<&PyFrozenSet>(py) {
                Box::new(frozenset.iter())
            } else if let Ok(list) = file_membership_obj.extract::<&PyList>(py) {
                Box::new(list.iter())
            } else if let Ok(tuple) = file_membership_obj.extract::<&PyTuple>(py) {
                let bool_item = tuple.get_item(0).and_then(|item| item.extract::<&PyBool>());
                let fs = tuple
                    .get_item(1)
                    .and_then(|item| item.extract::<&PyFrozenSet>());
                if let (2, Ok(_), Ok(fs_val)) = (tuple.len(), bool_item, fs) {
                    Box::new(fs_val.iter())
                } else {
                    return Err(PyTypeError::new_err(format!(
                        "argument 'file_membership': '{}' object cannot be converted to 'set' or 'list'",
                        file_membership_obj.as_ref(py).get_type().name()?
                    )));
                }
            } else if let Ok(value) = file_membership_obj.extract::<ArxmlFile>(py) {
                self.0
                    .set_file_membership([value.0.downgrade()].into_iter().collect());
                return Ok(());
            } else {
                return Err(PyTypeError::new_err(format!(
                    "argument 'file_membership': '{}' object cannot be converted to 'set' or 'list'",
                    file_membership_obj.as_ref(py).get_type().name()?
                )));
            };

            let mut fileset = HashSet::new();
            for item in iter {
                let weakfile = item.extract::<ArxmlFile>()?.0.downgrade();
                fileset.insert(weakfile);
            }
            self.0.set_file_membership(fileset);

            Ok(())
        })?;

        Ok(())
    }

    fn add_to_file(&self, file: &ArxmlFile) -> PyResult<()> {
        self.0
            .add_to_file(&file.0)
            .map_err(|error| AutosarDataError::new_err(error.to_string()))
    }

    fn remove_from_file(&self, file: &ArxmlFile) -> PyResult<()> {
        self.0
            .remove_from_file(&file.0)
            .map_err(|error| AutosarDataError::new_err(error.to_string()))
    }

    #[getter]
    fn xml_path(&self) -> String {
        self.0.xml_path()
    }
}