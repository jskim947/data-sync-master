@echo off
echo ========================================
echo 클라이언트 SSH 키 서버 등록
echo ========================================
echo.

echo 1. 기존 authorized_keys 백업...
if exist "%USERPROFILE%\.ssh\authorized_keys" (
    copy "%USERPROFILE%\.ssh\authorized_keys" "%USERPROFILE%\.ssh\authorized_keys.backup"
    echo 백업 완료: authorized_keys.backup
)

echo.
echo 2. 새로운 authorized_keys 파일 생성...
echo ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQDMZZEp2+5pXetTD1Wl5HEmjhx34EQ2SWATvuvBOaIt/w4rgQWWmx493fYTZcTxVF/FTl+ExpPoTOfEoBnTSGURXZ4SFmffX5wFhQJqNKZiLIKtmj6uHSOEJxQ1kZPuIhhNOab523264UsVTd6CBIGl4RZGFm54Gk0EhGSky20u5vQmdKHN4nliKBYTn5YonLTiZ/T+ZA1Mhmf2CG9+yEkqV837Hb2uGla3O2nc3uH6tuXAa45MUIfRZoLCPPDfNhTnA1PNJ1sl7+TeITDQ9f5/rfc52quTOxXuOp+rhwnaY5uB+qF9zGm9vOPTDU6tN4wStQi+BzkQ/GO0qZzHxjE6LSRIzipPGosLyfDdlEQLHpmUlRvSzYnXAhWRkacATP08Z3ripdEDJxWz+0e3cBpN0l/kb9fhkC+5C12fgp67eOJz2UVA1fGM5SXu7oormBcV58DIXdPaTg9JKXGUBGHv/w8pA/mR6knn3aQxHixGI7RAPL+jk390VsF8mshl8l+PCJpOnfO5OmFT7dCHtA7AisICIOaDljG5lUXT1hFni2Xc28yudwFOOpFh294TPuuL4VLlj51dQ7wjLBnsO0+RysbJ+nm22Orx data-sync-master@local > "%USERPROFILE%\.ssh\authorized_keys"

echo.
echo 3. 파일 권한 설정...
icacls "%USERPROFILE%\.ssh\authorized_keys" /inheritance:r
icacls "%USERPROFILE%\.ssh\authorized_keys" /grant:r "%USERNAME%:(F)"

echo.
echo 4. 설정 확인...
echo ========================================
echo 현재 authorized_keys 내용:
echo ========================================
type "%USERPROFILE%\.ssh\authorized_keys"
echo ========================================
echo.
echo ========================================
echo 클라이언트 SSH 키 등록 완료!
echo ========================================
echo.
echo 이제 클라이언트에서 다음으로 접속할 수 있습니다:
echo ssh infomax@10.150.2.150
echo.
echo 또는 VS Code Remote-SSH에서:
echo Host: 10.150.2.150
echo User: infomax
echo ======================================== 