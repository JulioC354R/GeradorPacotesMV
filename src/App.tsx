import { useState, useCallback } from 'react';
import { invoke } from '@tauri-apps/api/core';
import { listen } from '@tauri-apps/api/event';
import { open } from '@tauri-apps/plugin-dialog';

import { RepoSelector } from './components/RepoSelector';
import { FolderInfo } from './components/FolderInfo';
import { ArtefactSelector } from './components/ArtefactSelector';
import { SelectedList } from './components/SelectedList';
import { CodeInputs } from './components/CodeInputs';
import { ProcessDialog } from './components/ProcessDialog';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogHeader,
  AlertDialogTitle,
} from './components/ui/alert-dialog';
import { Button } from './components/ui/button';
import { Play, Eraser } from 'lucide-react';
import type { Artefact, RepoInfo } from './types/artefact';

export default function App() {
  const [repoPath, setRepoPath] = useState('');
  const [pastaPai, setPastaPai] = useState('');
  const [repoInfo, setRepoInfo] = useState<RepoInfo | null>(null);
  const [artefactType, setArtefactType] = useState('');
  const [artefacts, setArtefacts] = useState<Artefact[]>([]);
  const [selected, setSelected] = useState<Artefact[]>([]);
  const [codigo, setCodigo] = useState('');

  const [processing, setProcessing] = useState(false);
  const [progress, setProgress] = useState(0);
  const [statusText, setStatusText] = useState('');
  const [logs, setLogs] = useState<string[]>([]);
  const [alert, setAlert] = useState<{ title: string; message: string } | null>(
    null,
  );

  const handleSelectRepo = useCallback(async () => {
    const folder = await open({ directory: true });
    if (folder) {
      setRepoPath(folder);
      setArtefacts([]);
      setArtefactType('');
      setRepoInfo(null);
      try {
        const info: RepoInfo = await invoke('get_repo_info', {
          repoPath: folder,
        });
        setRepoInfo(info);
      } catch (e) {
        setAlert({ title: 'Erro', message: String(e) });
      }
    }
  }, []);

  const handleTypeChange = useCallback(
    async (type: string) => {
      setArtefactType(type);
      if (!repoPath) return;
      try {
        const list: Artefact[] = await invoke('list_artefacts', {
          repoPath,
          artefactType: type,
        });
        setArtefacts(list);
      } catch (e) {
        setAlert({ title: 'Erro', message: String(e) });
      }
    },
    [repoPath],
  );

  const handleArtefactAdd = useCallback((a: Artefact) => {
    setSelected((prev) =>
      prev.find((x) => x.path === a.path)
        ? prev
        : [...prev, a],
    );
  }, []);

  const handleArtefactRemove = useCallback((a: Artefact) => {
    setSelected((prev) =>
      prev.filter((x) => x.path !== a.path),
    );
  }, []);

  const handleProcess = useCallback(async () => {
    if (!repoPath && !selected.length) {
      setAlert({ title: 'Erro', message: 'Selecione um repositório.' });
      return;
    }
    if (!pastaPai) {
      setAlert({ title: 'Erro', message: 'Informe a Torre.' });
      return;
    }
    if (!selected.length) {
      setAlert({ title: 'Erro', message: 'Selecione ao menos um artefato.' });
      return;
    }

    setProcessing(true);
    setProgress(0);
    setStatusText('Iniciando processamento...');
    setLogs(['Iniciando processamento...']);

    const unlisten1 = await listen<string>('log-line', (event) => {
      setLogs((prev) => [...prev.slice(-999), event.payload]);
    });
    const unlisten2 = await listen<number>('progress', (event) => {
      setProgress(event.payload);
    });
    const unlisten3 = await listen<string>('status', (event) => {
      setStatusText(event.payload);
    });

    try {
      const success: boolean = await invoke('process_artefacts', {
        artefacts: selected,
        codigo: codigo || null,
        pastaPai,
      });
      if (success) {
        setAlert({ title: 'Sucesso', message: 'Processamento concluído!' });
      } else {
        setAlert({ title: 'Falha', message: 'GERAÇÃO FALHOU!' });
      }
    } catch (e) {
      setAlert({ title: 'Erro', message: String(e) });
    } finally {
      setProcessing(false);
      unlisten1();
      unlisten2();
      unlisten3();
    }
  }, [selected, pastaPai, codigo, repoPath]);

  const handleClear = useCallback(() => {
    setRepoPath('');
    setPastaPai('');
    setArtefactType('');
    setArtefacts([]);
    setSelected([]);
    setCodigo('');
    setLogs([]);
    setProgress(0);
    setStatusText('');
    setRepoInfo(null);
  }, []);

  const modulesInPackage = new Map<string, string>();
  for (const a of selected) {
    if (!modulesInPackage.has(a.module)) {
      modulesInPackage.set(a.module, a.version);
    }
  }

  return (
    <div className="grid grid-rows-[auto_1fr_auto] gap-3 p-4 h-screen overflow-hidden max-w-4xl mx-auto">
      <div className="flex flex-col gap-3 min-h-0">
        <RepoSelector value={repoPath} onSelect={handleSelectRepo} />
        <FolderInfo
          pastaPai={pastaPai}
          currentRepoInfo={repoInfo}
          modulesInPackage={modulesInPackage}
          onPastaPaiChange={setPastaPai}
        />
        {repoPath && (
          <ArtefactSelector
            artefactType={artefactType}
            artefacts={artefacts}
            onTypeChange={handleTypeChange}
            onArtefactAdd={handleArtefactAdd}
          />
        )}
        <CodeInputs codigo={codigo} onCodigoChange={setCodigo} />
      </div>

      <div className="overflow-y-auto min-h-0">
        <SelectedList artefacts={selected} onRemove={handleArtefactRemove} />
      </div>

      <div className="flex justify-end gap-2 pt-2">
        <Button variant="destructive" size="sm" onClick={handleClear}>
          <Eraser className="h-3 w-3" /> Limpar
        </Button>
        <Button
          size="sm"
          onClick={handleProcess}
          disabled={processing}
          className="bg-green-600 hover:bg-green-700 text-white"
        >
          <Play className="h-3 w-3" /> Processar
        </Button>
      </div>

      <ProcessDialog
        open={processing}
        progress={progress}
        statusText={statusText}
        logs={logs}
      />

      <AlertDialog open={!!alert} onOpenChange={() => setAlert(null)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>{alert?.title}</AlertDialogTitle>
            <AlertDialogDescription>{alert?.message}</AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogAction onClick={() => setAlert(null)}>
            OK
          </AlertDialogAction>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}
