import { Input } from "./ui/input"
import { Button } from "./ui/button"
import { FolderOpen } from "lucide-react"

interface RepoSelectorProps {
  value: string
  onSelect: () => void
}

export function RepoSelector({ value, onSelect }: RepoSelectorProps) {
  return (
    <div className="flex gap-2">
      <Input value={value} readOnly placeholder="Pasta do repositório" className="flex-1" />
      <Button variant="outline" size="icon" onClick={onSelect} title="Selecionar repositório">
        <FolderOpen className="h-4 w-4 text-blue-500" />
      </Button>
    </div>
  )
}
