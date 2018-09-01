import universityExtractor as U_ex
import studentExtractor as S_ex

url = "https://yocket.in/applications-admits-rejects/university-of-connecticut/2?page=5"
token,session = S_ex.getAuthSession()
soup = U_ex.open_url_2_soup(url, session_request = session)