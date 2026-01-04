from .database import SessionLocal
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")

def format_large_number(value):
    if value is None:
        return "0"
    try:
        num = float(value)
    except (ValueError, TypeError):
        return str(value)
        
    if num >= 1_000_000:
        return f"{num/1_000_000:.1f}M"
    elif num >= 100_000:
        return f"{num/1_000:.0f}K"
    else:
        if num % 1 == 0:
            return str(int(num))
        return f"{num:.2f}"

templates.env.filters["format_large_number"] = format_large_number

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
