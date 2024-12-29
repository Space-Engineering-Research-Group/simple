import xlwings as xw
import os

file_path = r"C:/Users/pekko/OneDrive/ドキュメント/rog.xlsx"

def open_workbook():
    app = xw.App(visible=True)
    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"指定されたファイル {file_path} が見つかりません。")
        workbook = app.books.open(file_path)
        sheet = workbook.sheets[0]
        return app, workbook, sheet
    except Exception as e:
        app.quit()
        raise e


def delete():
    if workbook in locals() and workbook is not None:
        workbook.save()
    if workbook in locals() and workbook is not None:
        workbook.close()  # workbook を閉じる
    if app in locals() and app is not None:
        app.quit()