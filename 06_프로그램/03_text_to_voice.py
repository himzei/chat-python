"""
텍스트를 음성으로 변환하는 프로그램
pyttsx3 라이브러리를 사용하여 텍스트를 음성으로 변환합니다.
"""

import pyttsx3
import sys


def 텍스트_음성_변환(텍스트, 속도=None, 볼륨=None, 음성_인덱스=None):
    """
    텍스트를 음성으로 변환하는 함수
    
    Args:
        텍스트 (str): 변환할 텍스트
        속도 (int): 말하기 속도 (기본값: 200, 범위: 50-300)
        볼륨 (float): 볼륨 (기본값: 1.0, 범위: 0.0-1.0)
        음성_인덱스 (int): 사용할 음성 인덱스 (None이면 기본 음성 사용)
    
    Returns:
        bool: 성공 여부
    """
    try:
        # TTS 엔진 초기화
        엔진 = pyttsx3.init()
        
        # 속도 설정 (기본값: 200)
        if 속도 is not None:
            엔진.setProperty('rate', 속도)
        else:
            엔진.setProperty('rate', 200)
        
        # 볼륨 설정 (기본값: 1.0)
        if 볼륨 is not None:
            엔진.setProperty('volume', 볼륨)
        else:
            엔진.setProperty('volume', 1.0)
        
        # 음성 선택 (한국어 음성이 있다면 사용)
        음성_목록 = 엔진.getProperty('voices')
        if 음성_인덱스 is not None and 0 <= 음성_인덱스 < len(음성_목록):
            엔진.setProperty('voice', 음성_목록[음성_인덱스].id)
        
        # 텍스트를 음성으로 변환
        엔진.say(텍스트)
        엔진.runAndWait()
        
        return True
    
    except Exception as 오류:
        print(f"오류 발생: {오류}")
        return False


def 사용_가능한_음성_목록_출력():
    """사용 가능한 음성 목록을 출력하는 함수"""
    try:
        엔진 = pyttsx3.init()
        음성_목록 = 엔진.getProperty('voices')
        
        print("\n=== 사용 가능한 음성 목록 ===")
        for 인덱스, 음성 in enumerate(음성_목록):
            print(f"{인덱스}: {음성.name} ({음성.languages})")
        print()
    
    except Exception as 오류:
        print(f"음성 목록을 가져오는 중 오류 발생: {오류}")


def 메인():
    """메인 함수"""
    print("=" * 50)
    print("텍스트를 음성으로 변환하는 프로그램")
    print("=" * 50)
    
    # 사용 가능한 음성 목록 출력
    사용_가능한_음성_목록_출력()
    
    while True:
        print("\n옵션을 선택하세요:")
        print("1. 텍스트 직접 입력")
        print("2. 파일에서 텍스트 읽기")
        print("3. 예제 텍스트 사용")
        print("4. 음성 목록 다시 보기")
        print("5. 종료")
        
        선택 = input("\n선택 (1-5): ").strip()
        
        if 선택 == '1':
            텍스트 = input("\n변환할 텍스트를 입력하세요: ")
            if 텍스트.strip():
                속도_입력 = input("말하기 속도 (기본값: 200, Enter로 건너뛰기): ").strip()
                속도 = int(속도_입력) if 속도_입력 else None
                
                print("\n음성 변환 중...")
                텍스트_음성_변환(텍스트, 속도=속도)
                print("완료!")
            else:
                print("텍스트를 입력해주세요.")
        
        elif 선택 == '2':
            파일_경로 = input("\n파일 경로를 입력하세요: ").strip()
            try:
                with open(파일_경로, 'r', encoding='utf-8') as 파일:
                    텍스트 = 파일.read()
                
                if 텍스트.strip():
                    print("\n음성 변환 중...")
                    텍스트_음성_변환(텍스트)
                    print("완료!")
                else:
                    print("파일이 비어있습니다.")
            
            except FileNotFoundError:
                print(f"파일을 찾을 수 없습니다: {파일_경로}")
            except Exception as 오류:
                print(f"파일 읽기 오류: {오류}")
        
        elif 선택 == '3':
            예제_텍스트 = "안녕하세요. 이것은 텍스트를 음성으로 변환하는 예제입니다."
            print(f"\n예제 텍스트: {예제_텍스트}")
            print("음성 변환 중...")
            텍스트_음성_변환(예제_텍스트)
            print("완료!")
        
        elif 선택 == '4':
            사용_가능한_음성_목록_출력()
        
        elif 선택 == '5':
            print("\n프로그램을 종료합니다.")
            break
        
        else:
            print("\n잘못된 선택입니다. 1-5 사이의 숫자를 입력해주세요.")


if __name__ == "__main__":
    try:
        메인()
    except KeyboardInterrupt:
        print("\n\n프로그램이 사용자에 의해 중단되었습니다.")
        sys.exit(0)
    except Exception as 오류:
        print(f"\n예상치 못한 오류 발생: {오류}")
        sys.exit(1)
