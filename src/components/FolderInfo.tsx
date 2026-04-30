import { Input } from './ui/input';
import { Badge } from './ui/badge';

interface FolderInfoProps {
  pastaPai: string;
  currentRepoInfo: { module: string; version: string } | null;
  modulesInPackage: Map<string, string>;
  onPastaPaiChange: (value: string) => void;
}

export function FolderInfo({
  pastaPai,
  currentRepoInfo,
  modulesInPackage,
  onPastaPaiChange,
}: FolderInfoProps) {
  return (
    <div className="flex flex-col gap-2">
      <Input
        placeholder="TORRE (ex: FINAN, CONTR)"
        value={pastaPai}
        onChange={(e) => onPastaPaiChange(e.target.value.toUpperCase())}
        maxLength={20}
      />
      <div className="flex flex-wrap items-center gap-2 min-h-[28px]">
        <span className="text-xs text-muted-foreground">
          Repositório atual:
        </span>
        {currentRepoInfo ? (
          <>
            <Badge variant="outline" className="text-xs">
              {currentRepoInfo.module}
            </Badge>
            <Badge variant="secondary" className="text-xs">
              {currentRepoInfo.version}
            </Badge>
          </>
        ) : (
          <span className="text-xs text-muted-foreground italic">
            Nenhum repositório selecionado
          </span>
        )}
        {modulesInPackage.size > 0 && (
          <>
            <span className="text-xs text-muted-foreground ml-1">
              Módulos no pacote:
            </span>
            {Array.from(modulesInPackage.entries()).map(([mod, ver]) => (
              <Badge key={mod} variant="default" className="text-xs">
                {mod} ({ver})
              </Badge>
            ))}
          </>
        )}
      </div>
    </div>
  );
}
