import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from "./ui/dialog"
import { Progress } from "./ui/progress"

interface ProcessDialogProps {
  open: boolean
  progress: number
  statusText: string
  logs: string[]
}

export function ProcessDialog({ open, progress, statusText, logs }: ProcessDialogProps) {
  return (
    <Dialog open={open}>
      <DialogContent className="sm:max-w-lg">
        <DialogHeader>
          <DialogTitle>Processando artefatos</DialogTitle>
          <DialogDescription>{statusText}</DialogDescription>
        </DialogHeader>
        <Progress value={progress} className="w-full" />
        <div className="max-h-[200px] overflow-y-auto border rounded p-2 bg-muted/50 text-xs font-mono space-y-1">
          {logs.map((line, i) => (
            <p key={i} className="leading-tight">{line}</p>
          ))}
        </div>
      </DialogContent>
    </Dialog>
  )
}
