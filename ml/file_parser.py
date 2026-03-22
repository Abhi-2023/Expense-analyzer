import pandas as pd
import pdfplumber
from fastapi import HTTPException

def parse_csv(filepath:str) -> list[dict]:
    try:
        df = pd.read_csv(filepath)
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f'Could not read csv file :{str(e)}'
        ) from e
    df.columns = df.columns.str.strip().str.lower()

    required_columns = {'description', 'amount', 'account_number'}
    if not required_columns.issubset(df.columns):
        raise HTTPException(
            status_code=400,
            detail=f"Your file must contain description, amount, account_number. Found:{list(df.columns)}"
        )

    df = df[["description", "amount", "account_number"]]
    df["description"] = df["description"].astype(str).str.strip()
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
    df["account_number"] = df["account_number"].astype(str).str.strip()
    df = df.dropna(subset=["description", "amount"])
    df = df[df["description"] != ""]

    return df.to_dict(orient="records")


def parse_excel(filepath: str) -> list[dict]:
    try:
        df = pd.read_excel(filepath, engine="openpyxl")
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Could not read Excel file: {str(e)}"
        ) from e

    df.columns = df.columns.str.strip().str.lower()

    required_columns = {"description", "amount", "account_number"}
    if not required_columns.issubset(df.columns):
        raise HTTPException(
            status_code=400,
            detail=f"Excel must contain columns: description, amount, account_number. Found: {list(df.columns)}"
        )

    df = df[["description", "amount", "account_number"]]
    df["description"] = df["description"].astype(str).str.strip()
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
    df["account_number"] = df["account_number"].astype(str).str.strip()
    df = df.dropna(subset=["description", "amount"])
    df = df[df["description"] != ""]

    return df.to_dict(orient="records")

def parse_pdf(filepath: str) -> list[dict]:
    all_rows = []

    try:
        with pdfplumber.open(filepath) as pdf:
            for page in pdf.pages:
                table = page.extract_table()

                if not table:
                    continue

                for row in table:
                    if not row or not row[0]:
                        continue

                    parts = row[0].strip().split()

                    if len(parts) < 3:
                        continue

                    account_number = parts[-1]
                    amount = parts[-2]
                    description = " ".join(parts[:-2])

                    if description.lower() == "description":
                        continue

                    all_rows.append({
                        "description": description,
                        "amount": amount,
                        "account_number": account_number
                    })

    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Could not read PDF file: {str(e)}"
        ) from e

    if not all_rows:
        raise HTTPException(
            status_code=400,
            detail="No table found in PDF. Make sure your bank statement contains a proper table."
        )

    df = pd.DataFrame(all_rows)
    df["description"] = df["description"].astype(str).str.strip()
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
    df["account_number"] = df["account_number"].astype(str).str.strip()
    df = df.dropna(subset=["description", "amount"])
    df = df[df["description"] != ""]

    return df.to_dict(orient="records")

def parse_file(filepath: str) -> list[dict]:
    if filepath.endswith(".csv"):
        return parse_csv(filepath)
    elif filepath.endswith(".xlsx"):
        return parse_excel(filepath)
    elif filepath.endswith(".pdf"):
        return parse_pdf(filepath)
    else:
        raise HTTPException(status_code=400, detail="Unsupported file type")