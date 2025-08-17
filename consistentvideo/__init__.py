import logging

# 기본 로깅 설정: 상위(루트) 로거에 핸들러가 없을 때만 설정
if not logging.getLogger().handlers:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )


