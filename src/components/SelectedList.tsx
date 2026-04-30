import { X } from "lucide-react"
import { Badge } from "./ui/badge"
import type { Artefact } from "../types/artefact"

interface SelectedListProps {
  artefacts: Artefact[]
  onRemove: (artefact: Artefact) => void
}

export function SelectedList({ artefacts, onRemove }: SelectedListProps) {
  if (artefacts.length === 0) return null

  // Group by module
  const groups = new Map<string, Artefact[]>()
  for (const a of artefacts) {
    const list = groups.get(a.module) || []
    list.push(a)
    groups.set(a.module, list)
  }

  return (
    <div>
      <p className="text-sm text-muted-foreground mb-2">Artefatos selecionados:</p>
      {Array.from(groups.entries()).map(([module, items]) => (
        <div key={module} className="mb-2">
          <p className="text-xs font-semibold text-muted-foreground mb-1">{module} ({items[0].version})</p>
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-2">
            {items.map((a) => (
              <Badge key={a.name + a.module} variant="secondary" className="justify-between gap-1">
                <span className="truncate text-xs" title={a.path}>{a.name}</span>
                <button onClick={() => onRemove(a)} className="hover:text-destructive">
                  <X className="h-3 w-3" />
                </button>
              </Badge>
            ))}
          </div>
        </div>
      ))}
    </div>
  )
}
