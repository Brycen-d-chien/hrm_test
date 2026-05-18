import pytest
from backend.domain.s3_service import S3DomainService, ALLOWED_FOLDERS, MAX_FILE_SIZE_BYTES
from backend.domain.storage_entity import S3ValidationError


class TestValidateUpload:
    def setup_method(self):
        self.service = S3DomainService()

    def test_passes_for_valid_input(self):
        self.service.validate_upload(1, "avatars", "photo.jpg", 1024, "image/jpeg")

    def test_raises_for_disallowed_folder(self):
        with pytest.raises(S3ValidationError, match="Folder"):
            self.service.validate_upload(1, "invoices", "file.pdf", 1024, "application/pdf")

    def test_raises_for_zero_size(self):
        with pytest.raises(S3ValidationError, match="rỗng"):
            self.service.validate_upload(1, "documents", "file.pdf", 0, "application/pdf")

    def test_raises_for_negative_size(self):
        with pytest.raises(S3ValidationError, match="rỗng"):
            self.service.validate_upload(1, "documents", "file.pdf", -1, "application/pdf")

    def test_raises_when_size_exceeds_limit(self):
        over_limit = MAX_FILE_SIZE_BYTES + 1
        with pytest.raises(S3ValidationError, match="vượt quá"):
            self.service.validate_upload(1, "documents", "big.pdf", over_limit, "application/pdf")

    def test_passes_at_exact_size_limit(self):
        self.service.validate_upload(1, "documents", "file.pdf", MAX_FILE_SIZE_BYTES, "application/pdf")

    def test_raises_for_filename_with_special_chars(self):
        with pytest.raises(S3ValidationError, match="ký tự"):
            self.service.validate_upload(1, "documents", "file<script>.pdf", 100, "application/pdf")

    def test_raises_for_empty_filename(self):
        with pytest.raises(S3ValidationError, match="ký tự"):
            self.service.validate_upload(1, "avatars", "", 100, "image/jpeg")

    def test_all_allowed_folders_pass(self):
        for folder in ALLOWED_FOLDERS:
            self.service.validate_upload(1, folder, "file.pdf", 512, "application/pdf")


class TestBuildObjectKey:
    def setup_method(self):
        self.service = S3DomainService()

    def test_builds_correct_key_pattern(self):
        key = self.service.build_object_key(42, "documents", "contract.pdf")
        assert key == "documents/employee_42/contract.pdf"

    def test_replaces_spaces_with_underscore(self):
        key = self.service.build_object_key(1, "avatars", "my photo.jpg")
        assert key == "avatars/employee_1/my_photo.jpg"

    def test_strips_leading_trailing_spaces(self):
        key = self.service.build_object_key(1, "avatars", " photo.jpg ")
        assert key == "avatars/employee_1/photo.jpg"


class TestBuildFolderPrefix:
    def setup_method(self):
        self.service = S3DomainService()

    def test_builds_prefix_ending_with_slash(self):
        prefix = self.service.build_folder_prefix(5, "documents")
        assert prefix == "documents/employee_5/"

    def test_prefix_matches_key_start(self):
        prefix = self.service.build_folder_prefix(5, "documents")
        key = self.service.build_object_key(5, "documents", "file.pdf")
        assert key.startswith(prefix)
