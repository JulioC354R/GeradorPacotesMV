import { useState } from "react"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./ui/select"
import { Input } from "./ui/input"
import { Button } from "./ui/button"
import { Popover, PopoverContent, PopoverTrigger } from "./ui/popover"
import { Check, ChevronsUpDown } from "lucide-react"
import { cn } from "../lib/utils"
import type { Artefact } from "../types/artefact"

interface ArtefactSelectorProps {
  artefactType: string
  artefacts: Artefact[]
  onTypeChange: (type: string) => void
  onArtefactAdd: (artefact: Artefact) => void
}

export function ArtefactSelector({ artefactType, artefacts, onTypeChange, onArtefactAdd }: ArtefactSelectorProps) {
  const [open, setOpen] = useState(false)
  const [search, setSearch] = useState("")

  const filtered = artefacts.filter((a) =>
    a.name.toLowerCase().includes(search.toLowerCase())
  )

  return (
    <div className="flex gap-2">
      <Select value={artefactType} onValueChange={onTypeChange}>
        <SelectTrigger className="w-40">
          <SelectValue placeholder="Selecione o tipo" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="Forms">Forms</SelectItem>
          <SelectItem value="Reports">Reports</SelectItem>
          <SelectItem value="Libs">Libs</SelectItem>
        </SelectContent>
      </Select>

      <Popover open={open} onOpenChange={setOpen}>
        <PopoverTrigger asChild>
          <Button variant="outline" role="combobox" aria-expanded={open} className="flex-1 justify-between">
            {artefactType ? "Selecione o artefato..." : "Selecione um tipo primeiro"}
            <ChevronsUpDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
          </Button>
        </PopoverTrigger>
        <PopoverContent className="w-[300px] p-2">
          <Input
            placeholder="Pesquisar artefato..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="mb-2"
          />
          <div className="max-h-[260px] overflow-auto">
            {filtered.length === 0 ? (
              <p className="text-sm text-muted-foreground p-2">Nenhum artefato encontrado</p>
            ) : (
              filtered.map((a) => (
                <button
                  key={a.name}
                  onClick={() => {
                    onArtefactAdd(a)
                    setSearch("")
                    setOpen(false)
                  }}
                  className={cn(
                    "relative flex w-full cursor-default select-none items-center rounded-sm px-2 py-1.5 text-sm outline-none hover:bg-accent hover:text-accent-foreground"
                  )}
                >
                  <Check className="mr-2 h-4 w-4 opacity-0" />
                  {a.name}
                </button>
              ))
            )}
          </div>
        </PopoverContent>
      </Popover>
    </div>
  )
}
