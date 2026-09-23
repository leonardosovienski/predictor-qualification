# Mantém o Windows acordado (sistema + tela) enquanto este processo viver.
# Pedido por processo via SetThreadExecutionState: não altera configurações de energia
# e deixa de valer quando o processo termina. Uso: powershell -File keep_awake.ps1 <minutos>
param([int]$Minutes = 120)
Add-Type -Namespace Win32 -Name Power -MemberDefinition '[DllImport("kernel32.dll")] public static extern uint SetThreadExecutionState(uint esFlags);'
# ES_CONTINUOUS | ES_SYSTEM_REQUIRED | ES_DISPLAY_REQUIRED
[Win32.Power]::SetThreadExecutionState([uint32]"0x80000003") | Out-Null
Start-Sleep -Seconds ($Minutes * 60)
