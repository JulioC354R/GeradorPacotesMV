import { Input } from "./ui/input"

interface CodeInputsProps {
  codigo: string
  onCodigoChange: (v: string) => void
}

export function CodeInputs({ codigo, onCodigoChange }: CodeInputsProps) {
  const sanitize = (value: string) => value.replace(/[\/\\:*?"<>|]/g, "")

  return (
    <Input
      placeholder="Código Jira/Cervello"
      value={codigo}
      onChange={(e) => onCodigoChange(sanitize(e.target.value))}
      maxLength={20}
    />
  )
}
