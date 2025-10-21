"""
Unit tests for inference module.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import tempfile
import os

from src.api.inference import MedicalTextClassifier, get_classifier


class TestMedicalTextClassifier:
    """Test cases for MedicalTextClassifier."""
    
    @pytest.mark.unit
    def test_initialization(self):
        """Test classifier initialization."""
        classifier = MedicalTextClassifier()
        assert classifier.model is None
        assert classifier.tokenizer is None
        assert classifier.label_encoder is None
        assert classifier.device is not None
        assert not classifier.is_loaded()
    
    @pytest.mark.unit
    def test_focus_group_names(self):
        """Test that focus group names are correctly defined."""
        classifier = MedicalTextClassifier()
        expected_groups = [
            "Cancers",
            "Cardiovascular Diseases",
            "Metabolic & Endocrine Disorders", 
            "Neurological & Cognitive Disorders",
            "Other Age-Related & Immune Disorders"
        ]
        assert classifier.focus_group_names == expected_groups
    
    @pytest.mark.unit
    def test_rule_based_classify_cancer(self):
        """Test rule-based classification for cancer-related text."""
        classifier = MedicalTextClassifier()
        
        cancer_texts = [
            "What are the treatment options for breast cancer?",
            "I was diagnosed with lung tumor",
            "Chemotherapy side effects",
            "Malignant growth in liver",
            "Oncology appointment scheduled"
        ]
        
        for text in cancer_texts:
            predicted_class, confidence = classifier._rule_based_classify(text)
            assert predicted_class == "Cancers"
            assert confidence == 0.85
    
    @pytest.mark.unit
    def test_rule_based_classify_cardiovascular(self):
        """Test rule-based classification for cardiovascular-related text."""
        classifier = MedicalTextClassifier()
        
        cardio_texts = [
            "I have chest pain and shortness of breath",
            "High blood pressure medication",
            "Heart attack symptoms",
            "Stroke prevention",
            "Cardiac surgery recovery"
        ]
        
        for text in cardio_texts:
            predicted_class, confidence = classifier._rule_based_classify(text)
            assert predicted_class == "Cardiovascular Diseases"
            assert confidence == 0.80
    
    @pytest.mark.unit
    def test_rule_based_classify_metabolic(self):
        """Test rule-based classification for metabolic/endocrine-related text."""
        classifier = MedicalTextClassifier()
        
        metabolic_texts = [
            "What are the symptoms of diabetes?",
            "Blood sugar monitoring",
            "Insulin injection technique",
            "Thyroid hormone levels",
            "Kidney disease progression"
        ]
        
        for text in metabolic_texts:
            predicted_class, confidence = classifier._rule_based_classify(text)
            assert predicted_class == "Metabolic & Endocrine Disorders"
            assert confidence == 0.80
    
    @pytest.mark.unit
    def test_rule_based_classify_neurological(self):
        """Test rule-based classification for neurological-related text."""
        classifier = MedicalTextClassifier()
        
        neuro_texts = [
            "My grandmother has Alzheimer's disease",
            "Parkinson's tremor management",
            "Memory loss concerns",
            "Brain scan results",
            "Cognitive decline symptoms"
        ]
        
        for text in neuro_texts:
            predicted_class, confidence = classifier._rule_based_classify(text)
            assert predicted_class == "Neurological & Cognitive Disorders"
            assert confidence == 0.75
    
    @pytest.mark.unit
    def test_rule_based_classify_other(self):
        """Test rule-based classification for other/default category."""
        classifier = MedicalTextClassifier()
        
        other_texts = [
            "General health checkup",
            "Vitamin deficiency",
            "Common cold symptoms",
            "Skin rash treatment",
            "Eye examination"
        ]
        
        for text in other_texts:
            predicted_class, confidence = classifier._rule_based_classify(text)
            assert predicted_class == "Other Age-Related & Immune Disorders"
            assert confidence == 0.60
    
    @pytest.mark.unit
    def test_rule_based_classify_case_insensitive(self):
        """Test that rule-based classification is case insensitive."""
        classifier = MedicalTextClassifier()
        
        test_cases = [
            ("DIABETES SYMPTOMS", "Metabolic & Endocrine Disorders"),
            ("Heart Disease", "Cardiovascular Diseases"),
            ("breast CANCER", "Cancers"),
            ("alzheimer's DISEASE", "Neurological & Cognitive Disorders")
        ]
        
        for text, expected_category in test_cases:
            predicted_class, confidence = classifier._rule_based_classify(text)
            assert predicted_class == expected_category
    
    @pytest.mark.unit
    def test_predict_without_model_loading(self):
        """Test prediction using rule-based approach without model loading."""
        classifier = MedicalTextClassifier()
        
        text = "What are the symptoms of diabetes?"
        predicted_class, confidence, probabilities = classifier.predict(text)
        
        assert predicted_class == "Metabolic & Endocrine Disorders"
        assert confidence == 0.80
        assert isinstance(probabilities, dict)
        assert len(probabilities) == 5
        assert all(0 <= prob <= 1 for prob in probabilities.values())
        
        # Check that probabilities sum to approximately 1
        total_prob = sum(probabilities.values())
        assert abs(total_prob - 1.0) < 0.01
        
        # Check that predicted class has highest probability
        max_prob_class = max(probabilities, key=probabilities.get)
        assert max_prob_class == predicted_class
    
    @pytest.mark.unit
    def test_predict_probability_distribution(self):
        """Test that prediction returns proper probability distribution."""
        classifier = MedicalTextClassifier()
        
        text = "Heart attack symptoms"
        predicted_class, confidence, probabilities = classifier.predict(text)
        
        # Check all focus groups are present
        for group in classifier.focus_group_names:
            assert group in probabilities
        
        # Check probabilities are normalized
        total_prob = sum(probabilities.values())
        assert abs(total_prob - 1.0) < 0.01
        
        # Check probabilities are sorted in descending order
        prob_values = list(probabilities.values())
        assert prob_values == sorted(prob_values, reverse=True)
    
    @pytest.mark.unit
    def test_predict_empty_text(self):
        """Test prediction with empty text."""
        classifier = MedicalTextClassifier()
        
        predicted_class, confidence, probabilities = classifier.predict("")
        
        # Should default to "Other" category
        assert predicted_class == "Other Age-Related & Immune Disorders"
        assert confidence == 0.60
        assert isinstance(probabilities, dict)
    
    @pytest.mark.unit
    def test_predict_whitespace_text(self):
        """Test prediction with whitespace-only text."""
        classifier = MedicalTextClassifier()
        
        predicted_class, confidence, probabilities = classifier.predict("   \n\t  ")
        
        # Should default to "Other" category
        assert predicted_class == "Other Age-Related & Immune Disorders"
        assert confidence == 0.60
    
    @pytest.mark.unit
    @patch('src.api.inference.logger')
    def test_predict_exception_handling(self, mock_logger):
        """Test that prediction handles exceptions gracefully."""
        classifier = MedicalTextClassifier()
        
        # Mock the _rule_based_classify method to raise an exception
        with patch.object(classifier, '_rule_based_classify', side_effect=Exception("Test error")):
            predicted_class, confidence, probabilities = classifier.predict("test text")
            
            # Should return default values
            assert predicted_class == "Other Age-Related & Immune Disorders"
            assert confidence == 0.1
            assert isinstance(probabilities, dict)
            assert len(probabilities) == 5
            
            # Should log the error
            mock_logger.error.assert_called_once()


class TestGetClassifier:
    """Test cases for get_classifier function."""
    
    @pytest.mark.unit
    def test_singleton_behavior(self):
        """Test that get_classifier returns the same instance."""
        classifier1 = get_classifier()
        classifier2 = get_classifier()
        
        assert classifier1 is classifier2
        assert isinstance(classifier1, MedicalTextClassifier)
    
    @pytest.mark.unit
    def test_classifier_type(self):
        """Test that get_classifier returns correct type."""
        classifier = get_classifier()
        assert isinstance(classifier, MedicalTextClassifier)


class TestClassifierModelLoading:
    """Test cases for model loading functionality."""
    
    @pytest.mark.unit
    @patch('src.api.inference.joblib.load')
    @patch('src.api.inference.AutoTokenizer.from_pretrained')
    @patch('src.api.inference.AutoModelForSequenceClassification.from_pretrained')
    @patch('os.path.exists')
    def test_load_model_success(self, mock_exists, mock_model, mock_tokenizer, mock_joblib):
        """Test successful model loading."""
        # Setup mocks
        mock_exists.return_value = True
        mock_label_encoder = Mock()
        mock_label_encoder.classes_ = ["class1", "class2", "class3"]
        mock_joblib.return_value = mock_label_encoder
        
        mock_tokenizer_instance = Mock()
        mock_tokenizer.return_value = mock_tokenizer_instance
        
        mock_model_instance = Mock()
        mock_model.return_value = mock_model_instance
        
        classifier = MedicalTextClassifier()
        classifier.load_model()
        
        # Verify model loading calls
        mock_joblib.assert_called_once()
        mock_tokenizer.assert_called_once()
        mock_model.assert_called_once()
        
        # Verify model is marked as loaded
        assert classifier.label_encoder == mock_label_encoder
        assert classifier.tokenizer == mock_tokenizer_instance
        assert classifier.model == mock_model_instance
    
    @pytest.mark.unit
    @patch('os.path.exists')
    def test_load_model_file_not_found(self, mock_exists):
        """Test model loading when files don't exist."""
        mock_exists.return_value = False
        
        classifier = MedicalTextClassifier()
        
        with pytest.raises(FileNotFoundError):
            classifier.load_model()
    
    @pytest.mark.unit
    @patch('src.api.inference.joblib.load')
    @patch('os.path.exists')
    def test_load_model_exception_handling(self, mock_exists, mock_joblib):
        """Test model loading exception handling."""
        mock_exists.return_value = True
        mock_joblib.side_effect = Exception("Failed to load")
        
        classifier = MedicalTextClassifier()
        
        with pytest.raises(Exception):
            classifier.load_model()
