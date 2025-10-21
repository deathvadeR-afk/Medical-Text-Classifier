"""
Unit tests for database module.
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.db import Base, MedicalText, init_db


class TestMedicalTextModel:
    """Test cases for MedicalText SQLAlchemy model."""
    
    @pytest.fixture
    def db_session(self):
        """Create a test database session."""
        engine = create_engine(
            "sqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        Base.metadata.create_all(engine)
        TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        session = TestingSessionLocal()
        yield session
        session.close()
    
    @pytest.mark.unit
    def test_create_medical_text(self, db_session):
        """Test creating a MedicalText record."""
        medical_text = MedicalText(
            question="What are the symptoms of diabetes?",
            answer="Common symptoms include increased thirst and frequent urination.",
            source="test_source",
            focusarea="Diabetes",
            focusgroup="Metabolic & Endocrine Disorders"
        )
        
        db_session.add(medical_text)
        db_session.commit()
        
        # Verify the record was created
        assert medical_text.id is not None
        assert medical_text.question == "What are the symptoms of diabetes?"
        assert medical_text.answer == "Common symptoms include increased thirst and frequent urination."
        assert medical_text.source == "test_source"
        assert medical_text.focusarea == "Diabetes"
        assert medical_text.focusgroup == "Metabolic & Endocrine Disorders"
        assert medical_text.created_at is not None
    
    @pytest.mark.unit
    def test_query_medical_text(self, db_session):
        """Test querying MedicalText records."""
        # Create test records
        records = [
            MedicalText(
                question="What causes heart disease?",
                answer="Heart disease can be caused by various factors.",
                source="cardiology",
                focusarea="Heart Disease",
                focusgroup="Cardiovascular Diseases"
            ),
            MedicalText(
                question="How is cancer diagnosed?",
                answer="Cancer diagnosis involves various tests and procedures.",
                source="oncology",
                focusarea="Cancer",
                focusgroup="Cancers"
            )
        ]
        
        for record in records:
            db_session.add(record)
        db_session.commit()
        
        # Query all records
        all_records = db_session.query(MedicalText).all()
        assert len(all_records) == 2
        
        # Query by focus group
        cardio_records = db_session.query(MedicalText).filter(
            MedicalText.focusgroup == "Cardiovascular Diseases"
        ).all()
        assert len(cardio_records) == 1
        assert cardio_records[0].question == "What causes heart disease?"
    
    @pytest.mark.unit
    def test_unique_question_constraint(self, db_session):
        """Test that question field has unique constraint."""
        # Create first record
        medical_text1 = MedicalText(
            question="What are the symptoms of diabetes?",
            answer="First answer",
            source="source1",
            focusarea="Diabetes",
            focusgroup="Metabolic & Endocrine Disorders"
        )
        db_session.add(medical_text1)
        db_session.commit()
        
        # Try to create second record with same question
        medical_text2 = MedicalText(
            question="What are the symptoms of diabetes?",  # Same question
            answer="Second answer",
            source="source2",
            focusarea="Diabetes",
            focusgroup="Metabolic & Endocrine Disorders"
        )
        db_session.add(medical_text2)
        
        # Should raise integrity error due to unique constraint
        with pytest.raises(Exception):  # SQLAlchemy will raise IntegrityError
            db_session.commit()
    
    @pytest.mark.unit
    def test_required_fields(self, db_session):
        """Test that required fields cannot be null."""
        # Test missing question
        with pytest.raises(Exception):
            medical_text = MedicalText(
                answer="Some answer",
                source="test",
                focusarea="Test",
                focusgroup="Test Group"
            )
            db_session.add(medical_text)
            db_session.commit()
        
        db_session.rollback()
        
        # Test missing answer
        with pytest.raises(Exception):
            medical_text = MedicalText(
                question="Some question?",
                source="test",
                focusarea="Test",
                focusgroup="Test Group"
            )
            db_session.add(medical_text)
            db_session.commit()
    
    @pytest.mark.unit
    def test_optional_fields(self, db_session):
        """Test that optional fields can be null."""
        medical_text = MedicalText(
            question="Test question?",
            answer="Test answer",
            # source, focusarea, focusgroup are optional
        )
        
        db_session.add(medical_text)
        db_session.commit()
        
        assert medical_text.id is not None
        assert medical_text.source is None
        assert medical_text.focusarea is None
        assert medical_text.focusgroup is None
    
    @pytest.mark.unit
    def test_field_lengths(self, db_session):
        """Test field length constraints."""
        # Test normal length fields
        medical_text = MedicalText(
            question="A" * 1000,  # Long question (Text field)
            answer="B" * 2000,    # Long answer (Text field)
            source="C" * 32,      # Max source length
            focusarea="D" * 256,  # Max focusarea length
            focusgroup="E" * 64   # Max focusgroup length
        )
        
        db_session.add(medical_text)
        db_session.commit()
        
        assert medical_text.id is not None
        assert len(medical_text.question) == 1000
        assert len(medical_text.answer) == 2000
        assert len(medical_text.source) == 32
        assert len(medical_text.focusarea) == 256
        assert len(medical_text.focusgroup) == 64
    
    @pytest.mark.unit
    def test_string_representation(self, db_session):
        """Test string representation of MedicalText model."""
        medical_text = MedicalText(
            question="What is hypertension?",
            answer="High blood pressure condition.",
            source="cardiology",
            focusarea="Hypertension",
            focusgroup="Cardiovascular Diseases"
        )
        
        db_session.add(medical_text)
        db_session.commit()
        
        # Test that the object can be converted to string without error
        str_repr = str(medical_text)
        assert isinstance(str_repr, str)
        assert len(str_repr) > 0
    
    @pytest.mark.unit
    def test_update_record(self, db_session):
        """Test updating a MedicalText record."""
        medical_text = MedicalText(
            question="What is diabetes?",
            answer="Original answer",
            source="endocrinology",
            focusarea="Diabetes",
            focusgroup="Metabolic & Endocrine Disorders"
        )
        
        db_session.add(medical_text)
        db_session.commit()
        
        # Update the record
        medical_text.answer = "Updated answer with more details"
        medical_text.source = "updated_source"
        db_session.commit()
        
        # Verify the update
        updated_record = db_session.query(MedicalText).filter(
            MedicalText.question == "What is diabetes?"
        ).first()
        
        assert updated_record.answer == "Updated answer with more details"
        assert updated_record.source == "updated_source"
    
    @pytest.mark.unit
    def test_delete_record(self, db_session):
        """Test deleting a MedicalText record."""
        medical_text = MedicalText(
            question="What is cancer?",
            answer="Cancer is a group of diseases.",
            source="oncology",
            focusarea="Cancer",
            focusgroup="Cancers"
        )
        
        db_session.add(medical_text)
        db_session.commit()
        
        record_id = medical_text.id
        
        # Delete the record
        db_session.delete(medical_text)
        db_session.commit()
        
        # Verify the record is deleted
        deleted_record = db_session.query(MedicalText).filter(
            MedicalText.id == record_id
        ).first()
        
        assert deleted_record is None


class TestDatabaseInitialization:
    """Test cases for database initialization."""
    
    @pytest.mark.unit
    def test_init_db_function(self):
        """Test that init_db function works without errors."""
        # This test uses an in-memory SQLite database
        from sqlalchemy import create_engine, inspect
        from unittest.mock import patch

        test_engine = create_engine("sqlite:///:memory:")

        with patch('src.db.engine', test_engine):
            # Should not raise any exceptions
            init_db()

            # Verify that tables were created
            inspector = inspect(test_engine)
            assert 'medical_texts' in inspector.get_table_names()
    
    @pytest.mark.unit
    def test_table_structure(self):
        """Test that the medical_texts table has correct structure."""
        from sqlalchemy import create_engine, inspect
        
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        
        inspector = inspect(engine)
        columns = inspector.get_columns('medical_texts')
        
        # Check that all expected columns exist
        column_names = [col['name'] for col in columns]
        expected_columns = ['id', 'question', 'answer', 'source', 'focusarea', 'focusgroup', 'created_at']
        
        for expected_col in expected_columns:
            assert expected_col in column_names
        
        # Check primary key
        pk_columns = inspector.get_pk_constraint('medical_texts')
        assert pk_columns['constrained_columns'] == ['id']
