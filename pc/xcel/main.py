import xlwings as xw
import os

class Xcel():
    def open_workbook(self,file_path):
        self.app = xw.App(visible=True)
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"指定されたファイル {file_path} が見つかりません。")
            self.workbook = self.app.books.open(file_path)
            sheet = self.workbook.sheets[0]
            return self.app, self.workbook, sheet
        except Exception as e:
            self.app.quit()
            raise e


    def delete(self):
        if self.workbook in locals() and self.workbook is not None:
            self.workbook.save()
        if self.workbook in locals() and self.workbook is not None:
            self.workbook.close()  # workbook を閉じる
        if self.app in locals() and self.app is not None:
            self.app.quit()