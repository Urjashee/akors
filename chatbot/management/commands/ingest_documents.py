from django.core.management.base import BaseCommand
from chatbot.services import ingest_documents


class Command(BaseCommand):
    help = "Ingest all PDF files from the documents/ folder into PGVector."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dir",
            type=str,
            default=None,
            help="Path to the directory containing PDFs. Defaults to <BASE_DIR>/documents/.",
        )

    def handle(self, *args, **options):
        self.stdout.write("Starting PDF ingestion...")
        try:
            result = ingest_documents(documents_dir=options.get("dir"))
            self.stdout.write(
                self.style.SUCCESS(
                    f"Done. Files processed: {result['files_processed']}, "
                    f"Chunks stored: {result['chunks_stored']}"
                )
            )
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Ingestion failed: {e}"))
            raise
