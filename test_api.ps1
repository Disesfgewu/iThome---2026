$body = '{"target_school":"国立台湾大学","target_major":"資訊工程學系","interview_mode":"頂大嚴謹模式","candidate_profile":{"target_school":"國立臺灣大學","target_major":"資訊工程學系"}}'
try {
    $response = Invoke-RestMethod -Uri 'http://localhost:8000/api/interview/setup' -Method POST -ContentType 'application/json; charset=utf-8' -Body ([System.Text.Encoding]::UTF8.GetBytes($body))
    Write-Host "SUCCESS"
    Write-Host "session_id: $($response.session_id)"
    Write-Host "first_question: $($response.first_question)"
} catch {
    Write-Host "ERROR: $($_.Exception.Message)"
    Write-Host "Response: $($_.ErrorDetails.Message)"
}
