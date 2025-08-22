
from db.database import Database

from langchain_core.tools import Tool
from langchain_core.tools import tool

@tool(name_or_callable="search_by_topic", description="Tìm kiếm sách theo chủ đề (CategoryName). Input: topic (str). Output: list các sách.")
def search_by_topic(topic):
    """
    Tìm kiếm sách theo chủ đề (CategoryName).

    Args:
        topic (str): Chủ đề cần tìm.

    Returns:
        list: Danh sách tuple (BookID, BookName, Content, CategoryName) có chủ đề chứa từ khóa topic.
    """
    db = Database()
    db.connect()
    query = """
        SELECT Book.BookID, Book.BookName, Book.Content, BookCategory.CategoryName
        FROM Book
        LEFT JOIN BookCategory ON Book.CategoryID = BookCategory.CategoryID
        WHERE BookCategory.CategoryName LIKE %s
    """
    db.cursor.execute(query, ("%" + topic + "%",))
    results = db.cursor.fetchall()
    db.close()
    return results

def search_by_content(keyword):
    """
    Tìm kiếm sách theo nội dung hoặc tên sách.

    Args:
        keyword (str): Từ khóa cần tìm.

    Returns:
        list: Danh sách tuple (BookID, BookName, Content, CategoryName) có nội dung hoặc tên sách chứa từ khóa keyword.
    """
    db = Database()
    db.connect()
    query = """
        SELECT Book.BookID, Book.BookName, Book.Content, BookCategory.CategoryName
        FROM Book
        LEFT JOIN BookCategory ON Book.CategoryID = BookCategory.CategoryID
        WHERE Book.Content LIKE %s OR Book.BookName LIKE %s
    """
    db.cursor.execute(query, ("%" + keyword + "%", "%" + keyword + "%"))
    results = db.cursor.fetchall()
    db.close()
    return results


# Khởi tạo 2 tool cho LangGraph
# book_search_by_topic_tool = Tool(
#     name="search_by_topic",
#     description="Tìm kiếm sách theo chủ đề (CategoryName). Input: topic (str). Output: list các sách.",
#     func=search_by_topic
# )

book_search_by_content_tool = Tool(
    name="search_by_content",
    description="Tìm kiếm sách theo nội dung hoặc tên sách. Input: keyword (str). Output: list các sách.",
    func=search_by_content
)
