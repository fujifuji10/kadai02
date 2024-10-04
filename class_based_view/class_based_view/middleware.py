#middoleware.py
import logging
from django.utils.deprecation import MiddlewareMixin
import time #現在時刻を取得する

application_logger = logging.getLogger('application-loger')
error_logger = logging.getLogger('error-loger')
performance_logger = logging.getLogger('performance-logger')

class MyMiddleware(MiddlewareMixin):
  
  def process_view(self, request, view_func, view_args, view_kwargs): #viewを呼び出す前に実行される
    application_logger.info(request.get_full_path()) #このクラスでミドルウェアを使ってviewが呼び出されるたびにログにどのpathのviewが呼び出されたのか確認ができる
    print(dir(request))
    
  def process_exception(self, request, exception):
    error_logger.error(exception, exc_info=True)
    
class PerformanceMiddleware(MiddlewareMixin):
  
  def process_view(self, request, view_func, view_args, view_kwargs):
    start_time = time.time()
    request.start_time = start_time #request.start_timeに追加した時間がviewを呼び出すまえに実行された時間で、
  
  def process_template_response(self, request, response): #レスポンスを実行する時に呼ばれる（viewを実行したあと)
    response_time = time.time() - request.start_time
    performance_logger.info(f'{request.get_full_path()}: {response_time}s') #performance_loggerを実行すると、リクエストでfull_pathを取得、レスポンス時間(ビョウ)を取得（ログとして出力）
    return response 
  #request.start_timeに追加した時間がviewを呼び出すまえに実行された時間で、呼び出した後にレスポンスを返す時に時間を取得して差分でviewの実行にどれだけ時間がかかったかを特定する