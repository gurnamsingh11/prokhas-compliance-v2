import os
import shutil


def delete_directories_from_paths(*paths):
    for path in paths:
        try:
            directory = os.path.dirname(path)

            if not directory:
                print(f"[SKIP] No directory in path: {path}")
                continue

            # Safety checks
            if directory in ["/", "C:\\"] or len(directory) < 3:
                print(f"[SKIP] Unsafe directory: {directory}")
                continue

            if os.path.exists(directory) and os.path.isdir(directory):
                shutil.rmtree(directory)
                print(f"[DELETED] {directory}")
            else:
                print(f"[SKIP] Not found: {directory}")

        except Exception as e:
            print(f"[ERROR] {path} -> {e}")


settings = {
    "interest_profit_validation": {
        "source": 6,
        "target": 3,
    },
    "purpose_financing_validation": {
        "source": 4,
        "target": 4,
    },
    "facility_amount_validation": {
        "source": 1,
        "target": 1,
    },
    "customer_credit_records_validation": {
        "source": 5,
        "target": 1,
    },
    "legal_scoring": {"source": 4, "target": 6},
    "borrower_bankruptcy_validation": {"source": 1},
}
