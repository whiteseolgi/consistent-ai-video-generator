import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:file_picker/file_picker.dart';
import 'package:excel/excel.dart';
import 'package:video_player/video_player.dart';
import 'package:url_launcher/url_launcher.dart';
import 'package:flutter/foundation.dart' show kIsWeb;
import 'package:universal_html/html.dart' as html;

void main() {
  runApp(const ConsistentAIVideoApp());
}

class AppState extends ChangeNotifier{
  String synopsis = '';
  String storyScript = '';

  List<EntityItem> entities = [];
  List<SceneInfo> scenes = [];
  VideoResult? video;

  Future<void> analyzeSynopsisToEntities() async {
  // TODO: 엔티티 생성해서 엔티티 리스트 결정 필요
    await Future<void>.delayed(const Duration(milliseconds: 200));
    entities = const [
      EntityItem(name: '버스기사', type: '인물',
        imageUrl: 'https://picsum.photos/seed/busdriver/480/360'),
      EntityItem(name: '할아버지', type: '인물',
        imageUrl: 'https://picsum.photos/seed/grandpa/480/360'),
      EntityItem(name: '버스 하차벨', type: '사물',
        imageUrl: 'https://picsum.photos/seed/bell/480/360'),
      EntityItem(name: '청년 승객', type: '인물',
        imageUrl: 'https://picsum.photos/seed/young/480/360'),
    ];
    notifyListeners();
  }

  Future<void> analyzeScriptToScenes() async {
    // TODO: 씬/컷 캐싱
    await Future<void>.delayed(const Duration(milliseconds: 200));
    scenes = const [
      SceneInfo(
        title: '씬 1: 전세 버스 내부',
        description:
            '아침 햇살이 유리창을 통해 들어오고, 기사와 승객들이 각자의 생각에 잠겨 있다.',
      ),
      SceneInfo(
        title: '씬 2: 첫 등장, 할아버지',
        description:
            '할아버지가 조심스레 하차벨을 눌러준다. 주변의 시선이 잠시 그에게 쏠린다.',
      ),
      SceneInfo(
        title: '씬 3: 반복되는 벨',
        description:
            '목적지에 가깝지만 하차벨이 연달아 울린다. 청년 승객이 창밖을 응시한다.',
      ),
    ];
    notifyListeners();
  }

  Future<void> generateVideo() async {
  await Future<void>.delayed(const Duration(milliseconds: 200));
  video = const VideoResult(
    id: 'vid_demo_001',
    title: '버스기사와 할아버지의 싸움',
    description: '스토리 기반으로 생성된 예시 영상입니다.',
    thumbnailUrl: 'https://picsum.photos/seed/videoThumb/960/540',
    // 공개 샘플 영상 URL (mp4) — 실제 생성 URL로 교체
    videoUrl: 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4',
  );
  notifyListeners();
}


}

class AppStateScope extends StatefulWidget{

  const AppStateScope({super.key, required this.child});
  final Widget child;

  static AppState of(BuildContext context) {
    final provider =
        context.dependOnInheritedWidgetOfExactType<_AppStateProvider>();
    assert(provider != null, '트리 없음');
    return provider!.notifier;
  }

  @override
  State<AppStateScope> createState() => _AppStateScopeState();

}

class _AppStateScopeState extends State<AppStateScope> {
  late final AppState _state;

  @override
  void initState() {
    super.initState();
    _state = AppState();
  }

  @override
  Widget build(BuildContext context) {
    return _AppStateProvider(notifier: _state, child: widget.child);
  }
}

class _AppStateProvider extends InheritedNotifier<AppState> {
  const _AppStateProvider({
    required AppState notifier,
    required Widget child,
  }) : super(notifier: notifier, child: child);

  @override
  AppState get notifier => super.notifier!;
}

class ConsistentAIVideoApp extends StatelessWidget {
  const ConsistentAIVideoApp({super.key});

  @override
  Widget build(BuildContext context) {
    return AppStateScope( 
      child: MaterialApp(
        debugShowCheckedModeBanner: false,
        title: '한결필름',
        theme: ThemeData(
          colorScheme: ColorScheme.fromSeed(seedColor: const Color(0xFF303F9F)),
          useMaterial3: true,
        ),
        initialRoute: '/',  // 첫 화면
        routes: {
          '/':        (_) => const WelcomePage(),
          '/synopsis':(_) => const SynopsisPage(),
          '/entity':  (_) => const EntityPage(),
          '/story':   (_) => const StoryPage(),
          '/scene':   (_) => const SceneAnalysisPage(),
          '/result':  (_) => const ResultPage(),
        },
      ),
    );
  }
}


class WelcomePage extends StatelessWidget {
  const WelcomePage({super.key});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Scaffold(
      body: Center(
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 900),
          child: Padding(
            padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 40),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                // 로고
                Semantics(
                  label: '한결필름 로고',
                  child: Image.asset(
                    'assets/hangyeolfilm_logo.png',
                    width: 240,
                    fit: BoxFit.contain,
                  ),
                ),
                const SizedBox(height: 32),

                // 시작하기 버튼
                SizedBox(
                  width: 220,
                  child: FilledButton.icon(
                    icon: const Icon(Icons.play_arrow),
                    label: const Padding(
                      padding: EdgeInsets.symmetric(vertical: 12.0),
                      child: Text('시작하기', style: TextStyle(fontSize: 18)),
                    ),
                    style: FilledButton.styleFrom(
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(14),
                      ),
                    ),
                    onPressed: () {
                      Navigator.pushReplacementNamed(context, '/synopsis');
                    },
                  ),
                ),

                const SizedBox(height: 16),

                Text(
                  '일관성을 유지한 AI 영상 생성기',
                  style: theme.textTheme.bodyMedium!
                      .copyWith(color: theme.colorScheme.onSurfaceVariant),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}


// ----------------------시놉시스 페이지---------------------------------------
class SynopsisPage extends StatefulWidget {
  const SynopsisPage({super.key});

  @override
  State<SynopsisPage> createState() => _SynopsisPageState();
}

class _SynopsisPageState extends State<SynopsisPage> {
  final TextEditingController _controller = TextEditingController();
  bool _loading = false;

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    final state = AppStateScope.of(context);
    // 시놉시스 백업
    if (_controller.text.isEmpty && state.synopsis.isNotEmpty) {
      _controller.text = state.synopsis;
    }
  }

  Future<void> _goNext() async {
    final state = AppStateScope.of(context);
    state.synopsis = _controller.text.trim();

    setState(() => _loading = true);        // 선택: 버튼 로딩 처리
    await state.analyzeSynopsisToEntities(); // 시놉시스 분석
    if (!mounted) return;
    setState(() => _loading = false);

    Navigator.pushNamed(context, '/entity'); 
  }

  Future<void> _pickAndFill() async {
    try {
      setState(() => _loading = true);

      final result = await FilePicker.platform.pickFiles(
        type: FileType.custom,
        allowedExtensions: ['xlsx', 'csv', 'txt'],
        withData: true, 
      );
      if (result == null) return;

      final file = result.files.single;
      final ext = (file.extension ?? '').toLowerCase();
      final Uint8List? bytes = file.bytes;

      if (bytes == null) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('이 플랫폼에선 withData: true가 필요합니다.')),
        );
        return;
      }

      String filled = '';
      if (ext == 'xlsx') {
        filled = _extractFromXlsx(bytes);
      } else {
        // csv/txt (기본 UTF-8 가정)
        filled = utf8.decode(bytes).trim();
      }

      if (filled.isNotEmpty) {
        _controller.text = filled;
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('파일에서 내용을 찾지 못했습니다.')),
        );
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('불러오기 실패: $e')),
      );
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  /// 엑셀(.xlsx)에서 시놉시스 텍스트 추출 규칙
  /// 1) 첫 행의 헤더가 'synopsis' 또는 '시놉시스'인 컬럼이 있으면, 해당 컬럼 아래 셀들을 줄바꿈으로 합침
  /// 2) 없으면 시트 전체 비어있지 않은 셀을 공백으로 합쳐 반환
  String _extractFromXlsx(Uint8List bytes) {
    final excel = Excel.decodeBytes(bytes);
    const headerKeys = {'synopsis', '시놉시스'};

    // 1) 헤더 탐색
    for (final sheetName in excel.tables.keys) {
      final sheet = excel.tables[sheetName]!;
      final rows = sheet.rows;
      if (rows.isEmpty) continue;

      final headers = rows.first
          .map((cell) => (cell?.value?.toString() ?? '').trim().toLowerCase())
          .toList();

      for (int c = 0; c < headers.length; c++) {
        if (headerKeys.contains(headers[c])) {
          final lines = <String>[];
          for (int r = 1; r < rows.length; r++) {
            final cell = rows[r][c];
            final v = (cell?.value?.toString() ?? '').trim();
            if (v.isNotEmpty) lines.add(v);
          }
          if (lines.isNotEmpty) return lines.join('\n');
        }
      }
    }

    // 2) 헤더 없으면 전체 합치기
    final buf = StringBuffer();
    for (final sheetName in excel.tables.keys) {
      final sheet = excel.tables[sheetName]!;
      for (final row in sheet.rows) {
        for (final cell in row) {
          final v = (cell?.value?.toString() ?? '').trim();
          if (v.isNotEmpty) buf.write('$v ');
        }
      }
    }
    return buf.toString().trim();
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Scaffold(
      appBar: AppBar(title: const Text('시놉시스 입력')),
      body: Center(
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 1100),
          child: Padding(
            padding: const EdgeInsets.all(24.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                // 1) 텍스트 입력
                Expanded(
                  child: TextField(
                    controller: _controller,
                    expands: true,
                    maxLines: null,
                    minLines: null,
                    decoration: const InputDecoration(
                      hintText: '이야기의 시놉시스를 입력하거나, 아래 "불러오기"로 파일에서 채우세요.',
                      border: OutlineInputBorder(),
                    ),
                  ),
                ),
                const SizedBox(height: 16),
                // 2) 다음으로 / 3) 불러오기
                Row(
                  children: [
                    FilledButton.icon(
                      icon: const Icon(Icons.arrow_right_alt),
                      label: const Text('다음으로'),
                      onPressed: _loading ? null : _goNext,
                    ),
                    const SizedBox(width: 12),
                    OutlinedButton.icon(
                      icon: _loading
                          ? const SizedBox(
                              height: 16, width: 16,
                              child: CircularProgressIndicator(strokeWidth: 2),
                            )
                          : const Icon(Icons.upload_file),
                      label: const Text('불러오기'),
                      onPressed: _loading ? null : _pickAndFill,
                    ),
                    const Spacer(),
                    Text(
                      '지원: .xlsx / .csv / .txt',
                      style: theme.textTheme.bodySmall!
                          .copyWith(color: theme.colorScheme.onSurfaceVariant),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

// ----------------------시놉시스 페이지 끝---------------------------------------


// ----------------------레퍼런스 미리보기 페이지------------------------------------


class EntityPage extends StatelessWidget {
  const EntityPage({super.key});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final items = AppStateScope.of(context).entities; // ★ 시놉시스에서 채워진 결과

    return Scaffold(
      body: Center(
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 1200),
          child: Padding(
            padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 32),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Image.asset('assets/hangyeolfilm_logo.png', width: 28, height: 28),
                    const SizedBox(width: 8),
                    Text('한결필름',
                        style: theme.textTheme.titleMedium!.copyWith(fontWeight: FontWeight.w700)),
                  ],
                ),
                const SizedBox(height: 24),

                // 제목/설명
                Text('이야기의 구성요소를 만들었어요',
                    textAlign: TextAlign.center,
                    style: theme.textTheme.headlineSmall!.copyWith(
                      color: theme.colorScheme.primary,
                      fontWeight: FontWeight.w800,
                    )),
                const SizedBox(height: 8),
                Text(
                  '입력한 시놉시스를 바탕으로 이야기의 구성요소를 생성했어요.\n확인해보세요!',
                  textAlign: TextAlign.center,
                  style: theme.textTheme.bodyMedium!
                      .copyWith(color: theme.colorScheme.onSurfaceVariant),
                ),
                const SizedBox(height: 24),
                Expanded(
                  child: items.isEmpty
                      ? const Center(child: Text('표시할 구성요소가 없습니다. 시놉시스에서 분석 후 이동하세요.'))
                      : LayoutBuilder(
                          builder: (context, c) {
                            int cross = 4;
                            if (c.maxWidth < 1100) cross = 3;
                            if (c.maxWidth < 820) cross = 2;
                            if (c.maxWidth < 520) cross = 1;
                            return GridView.builder(
                              gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
                                crossAxisCount: cross,
                                crossAxisSpacing: 16,
                                mainAxisSpacing: 16,
                                childAspectRatio: 4 / 3,
                              ),
                              itemCount: items.length,
                              itemBuilder: (_, i) => _EntityCard(item: items[i]),
                            );
                          },
                        ),
                ),
                const SizedBox(height: 16),
                Align(
                  alignment: Alignment.center,
                  child: SizedBox(
                    width: 240,
                    child: FilledButton(
                      onPressed: () => Navigator.pushNamed(context, '/story'),
                      child: const Text('이야기 동영상 만들기'),
                    ),
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}                

// ====== 엔티티 카드 ======
class _EntityCard extends StatelessWidget {
  const _EntityCard({required this.item});
  final EntityItem item;

  @override
  Widget build(BuildContext context) {
    return Card(
      clipBehavior: Clip.antiAlias,
      elevation: 0.5,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          // 이미지
          Expanded(
            child: AspectRatio(
              aspectRatio: 4 / 3,
              child: Image.network(item.imageUrl, fit: BoxFit.cover),
            ),
          ),
          // 라벨
          Padding(
            padding: const EdgeInsets.fromLTRB(12, 10, 12, 12),
            child: Text(
              item.label,
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
              style: Theme.of(context)
                  .textTheme
                  .bodyMedium!
                  .copyWith(fontWeight: FontWeight.w600),
            ),
          ),
        ],
      ),
    );
  }
}

// ----------------------레퍼런스 미리보기 페이지 끝------------------------------------


// ----------------------스토리 입력 페이지------------------------------------

class StoryPage extends StatefulWidget {
  const StoryPage({super.key});

  @override
  State<StoryPage> createState() => _StoryPageState();
}

class _StoryPageState extends State<StoryPage> {
  final TextEditingController _controller = TextEditingController();
  bool _loading = false;

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    final state = AppStateScope.of(context);
    // 스토리 백업
    if (_controller.text.isEmpty && state.storyScript.isNotEmpty) {
      _controller.text = state.storyScript;
    }
  }

  // 다음 단계로 이동
  Future<void> _goNext() async {
    final state = AppStateScope.of(context);
    state.storyScript = _controller.text.trim();

    // -----------------------------스토리 분석 및 씬/컷 생성------------------------------------

    // TODO : 백엔드 호출을 하든~ story모듈을 불러오든~

    // ----------------------------------------------------------------------------------------

    if (!mounted) return;
    Navigator.pushNamed(context, '/scene');
  }

  // 구성요소 세트 재선택(= 시놉시스 화면으로 복귀)
  void _reselectEntities() {
    final state = AppStateScope.of(context);
    // 현재 입력 중 스토리를 상태에 먼저 저장
    state.storyScript = _controller.text;
    // 시놉시스는 state.synopsis 에 이미 저장되어 있으므로 그대로 남아있음.
    Navigator.pushReplacementNamed(context, '/synopsis');
  }

  // 파일 불러와 스토리 입력창 채우기 (.xlsx / .csv / .txt)
  Future<void> _pickAndFill() async {
    try {
      setState(() => _loading = true);

      final result = await FilePicker.platform.pickFiles(
        type: FileType.custom,
        allowedExtensions: ['xlsx', 'csv', 'txt'],
        withData: true,
      );
      if (result == null) return;

      final file = result.files.single;
      final ext = (file.extension ?? '').toLowerCase();
      final Uint8List? bytes = file.bytes;

      if (bytes == null) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('이 플랫폼은 withData: true가 필요합니다.')),
        );
        return;
      }

      String text = '';
      if (ext == 'xlsx') {
        text = _extractFromXlsx(bytes);
      } else {
        text = utf8.decode(bytes).trim(); // csv/txt
      }

      if (text.isNotEmpty) {
        _controller.text = text;
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('파일에서 텍스트를 찾지 못했습니다.')),
        );
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('불러오기 실패: $e')),
      );
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  /// 엑셀(.xlsx)에서 스토리 텍스트 추출
  /// 규칙: 1) 헤더가 'story' 또는 '스토리'면 해당 컬럼을 줄바꿈으로 합침
  ///       2) 없으면 시트 전체 텍스트를 공백으로 합침
  String _extractFromXlsx(Uint8List bytes) {
    final excel = Excel.decodeBytes(bytes);
    const headers = {'story', '스토리'};

    for (final name in excel.tables.keys) {
      final sheet = excel.tables[name]!;
      final rows = sheet.rows;
      if (rows.isEmpty) continue;

      final head = rows.first
          .map((c) => (c?.value?.toString() ?? '').trim().toLowerCase())
          .toList();
      for (int c = 0; c < head.length; c++) {
        if (headers.contains(head[c])) {
          final lines = <String>[];
          for (int r = 1; r < rows.length; r++) {
            final v = (rows[r][c]?.value?.toString() ?? '').trim();
            if (v.isNotEmpty) lines.add(v);
          }
          if (lines.isNotEmpty) return lines.join('\n');
        }
      }
    }

    final buf = StringBuffer();
    for (final name in excel.tables.keys) {
      final sheet = excel.tables[name]!;
      for (final row in sheet.rows) {
        for (final cell in row) {
          final v = (cell?.value?.toString() ?? '').trim();
          if (v.isNotEmpty) buf.write('$v ');
        }
      }
    }
    return buf.toString().trim();
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final state = AppStateScope.of(context);

    // TODO : 미리보기 엔티티: 상태에 없으면 데모로 대체 -> 나중에 for문으로 돌릴 수 있음
    //-------------------------------------------------------------------------------
    final preview = state.entities.isNotEmpty
        ? state.entities
        : const [
            EntityItem(
              name: '버스기사', type: '인물',
              imageUrl: 'https://picsum.photos/seed/busdriver/480/360',
            ),
            EntityItem(
              name: '할아버지', type: '인물',
              imageUrl: 'https://picsum.photos/seed/grandpa/480/360',
            ),
            EntityItem(
              name: '버스 하차벨', type: '사물',
              imageUrl: 'https://picsum.photos/seed/bell/480/360',
            ),
            EntityItem(
              name: '청년 승객', type: '인물',
              imageUrl: 'https://picsum.photos/seed/young/480/360',
            ),
          ];
      //--------------------------------------------------------------------------------------

    return Scaffold(
      body: Center(
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 1100),
          child: Padding(
            padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 32),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                // 로고
                Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Image.asset('assets/hangyeolfilm_logo.png', width: 28, height: 28),
                    const SizedBox(width: 8),
                    Text('한결필름',
                        style: theme.textTheme.titleMedium!.copyWith(fontWeight: FontWeight.w700)),
                  ],
                ),
                const SizedBox(height: 16),

                // 타이틀
                Text('스토리',
                    textAlign: TextAlign.center,
                    style: theme.textTheme.headlineMedium!.copyWith(
                      color: theme.colorScheme.primary,
                      fontWeight: FontWeight.w800,
                    )),
                const SizedBox(height: 16),

                // 1. 엔티티 미리보기 (가로 스크롤)
                SizedBox(
                  height: 160,
                  child: ListView.separated(
                    scrollDirection: Axis.horizontal,
                    padding: const EdgeInsets.symmetric(horizontal: 8),
                    separatorBuilder: (_, __) => const SizedBox(width: 12),
                    itemCount: preview.length,
                    itemBuilder: (_, i) => _EntityChip(item: preview[i]),
                  ),
                ),

                const SizedBox(height: 12),

                // 2. 구성요소 세트 재선택 (시놉시스로)
                Align(
                  alignment: Alignment.centerLeft,
                  child: OutlinedButton.icon(
                    icon: const Icon(Icons.settings_backup_restore),
                    label: const Text('구성요소 세트 재선택'),
                    onPressed: _reselectEntities,
                  ),
                ),

                const SizedBox(height: 12),

                // 3. 스토리 입력창
                Expanded(
                  child: TextField(
                    controller: _controller,
                    expands: true,
                    maxLines: null,
                    minLines: null,
                    decoration: const InputDecoration(
                      hintText: '영상으로 만들 스토리를 여기에 입력하세요...',
                      border: OutlineInputBorder(),
                    ),
                  ),
                ),
                const SizedBox(height: 12),

                // 4. 다음으로 / 5. 불러오기
                Row(
                  children: [
                    FilledButton.icon(
                      icon: const Icon(Icons.arrow_right_alt),
                      label: const Text('다음으로'),
                      onPressed: _loading ? null : _goNext,
                    ),
                    const SizedBox(width: 12),
                    OutlinedButton.icon(
                      icon: _loading
                          ? const SizedBox(
                              height: 16, width: 16,
                              child: CircularProgressIndicator(strokeWidth: 2),
                            )
                          : const Icon(Icons.upload_file),
                      label: const Text('불러오기'),
                      onPressed: _loading ? null : _pickAndFill,
                    ),
                    const Spacer(),
                    Text('지원: .xlsx / .csv / .txt',
                        style: theme.textTheme.bodySmall!
                            .copyWith(color: theme.colorScheme.onSurfaceVariant)),
                  ],
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

// 엔티티 미리보기용 위젯
class _EntityChip extends StatelessWidget {
  const _EntityChip({required this.item});
  final EntityItem item;

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: 220,
      child: Card(
        clipBehavior: Clip.antiAlias,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Expanded(
              child: Image.network(item.imageUrl, fit: BoxFit.cover),
            ),
            Padding(
              padding: const EdgeInsets.fromLTRB(12, 8, 12, 12),
              child: Text(
                '${item.name} (${item.type})',
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
                style: Theme.of(context)
                    .textTheme
                    .bodyMedium!
                    .copyWith(fontWeight: FontWeight.w600),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

// ----------------------스토리 입력 페이지 끝------------------------------------

// ----------------------씬/컷 미리보기 페이지------------------------------------

class SceneAnalysisPage extends StatefulWidget {
  const SceneAnalysisPage({super.key});

  @override
  State<SceneAnalysisPage> createState() => _SceneAnalysisPageState();
}

class _SceneAnalysisPageState extends State<SceneAnalysisPage> {
  bool _busy = false;

  Future<void> _makeVideo() async {
    final state = AppStateScope.of(context);
    setState(() => _busy = true);

    // ----------------------------------------------------------------

    // TODO: 실제 백엔드 호출로 대체 / 비디오 생성
    await state.generateVideo();

    // ----------------------------------------------------------------
    if (!mounted) return;
    setState(() => _busy = false);
    Navigator.pushNamed(context, '/result');
  }

  void _goBack() {
    Navigator.pushReplacementNamed(context, '/story');
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final state = AppStateScope.of(context);

    // 스토리 분석 결과가 비어있으면 데모 세트로 보이기(백엔드 붙을 때 제거 가능)
    final scenes = state.scenes.isNotEmpty
        ? state.scenes
        : const [
            SceneInfo(
              title: '씬 1: 전세 버스 내부',
              description:
                  '아침 햇살이 유리창을 통해 들어오고, 기사와 승객들이 각자의 생각에 잠겨 있다.',
            ),
            SceneInfo(
              title: '씬 2: 첫 등장, 할아버지',
              description:
                  '할아버지가 조심스레 하차벨을 눌러준다. 주변의 시선이 잠시 그에게 쏠린다.',
            ),
            SceneInfo(
              title: '씬 3: 반복되는 벨',
              description:
                  '목적지에 가깝지만 하차벨이 연달아 울린다. 청년 승객이 창밖을 응시한다.',
            ),
          ];

    return Scaffold(
      body: Center(
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 1200),
          child: Padding(
            padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 32),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                // 상단 로고
                Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Image.asset('assets/hangyeolfilm_logo.png', width: 28, height: 28),
                    const SizedBox(width: 8),
                    Text('한결필름',
                        style: theme.textTheme.titleMedium!.copyWith(fontWeight: FontWeight.w700)),
                  ],
                ),
                const SizedBox(height: 20),

                // 제목 + 설명
                Text(
                  '이야기를 다음과 같이 구성했어요',
                  textAlign: TextAlign.start,
                  style: theme.textTheme.headlineSmall!.copyWith(
                    color: theme.colorScheme.primary,
                    fontWeight: FontWeight.w800,
                  ),
                ),
                const SizedBox(height: 6),
                Text(
                  '입력한 이야기를 아래와 같이 구성했어요. 각 카드의 내용을 확인해보세요.',
                  style: theme.textTheme.bodyMedium!
                      .copyWith(color: theme.colorScheme.onSurfaceVariant),
                ),
                const SizedBox(height: 16),

                // 상단 버튼들
                Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    FilledButton.icon(
                      icon: _busy
                          ? const SizedBox(
                              width: 16, height: 16,
                              child: CircularProgressIndicator(strokeWidth: 2),
                            )
                          : const Icon(Icons.movie_creation_outlined),
                      label: const Text('동영상으로 만들기'),
                      onPressed: _busy ? null : _makeVideo,
                      style: FilledButton.styleFrom(
                        padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 12),
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(24)),
                      ),
                    ),
                    const SizedBox(width: 12),
                    OutlinedButton(
                      onPressed: _busy ? null : _goBack,
                      child: const Text('이전으로'),
                    ),
                  ],
                ),
                const SizedBox(height: 20),

                // 씬 카드 리스트
                Expanded(
                  child: LayoutBuilder(
                    builder: (context, c) {
                      int cross = 3;
                      if (c.maxWidth < 1100) cross = 2;
                      if (c.maxWidth < 720) cross = 1;

                      return GridView.builder(
                        gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
                          crossAxisCount: cross,
                          crossAxisSpacing: 16,
                          mainAxisSpacing: 16,
                          childAspectRatio: 4 / 2.2,
                        ),
                        itemCount: scenes.length,
                        itemBuilder: (_, i) => _SceneCard(scene: scenes[i], index: i),
                      );
                    },
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

// 씬 카드 위젯
class _SceneCard extends StatelessWidget {
  const _SceneCard({required this.scene, required this.index});
  final SceneInfo scene;
  final int index;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Card(
      elevation: 0.5,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Expanded(
              child: Text(
                scene.description,
                maxLines: 6,
                overflow: TextOverflow.ellipsis,
                style: theme.textTheme.bodyMedium,
              ),
            ),
            const SizedBox(height: 10),
            Row(
              children: [
                const Icon(Icons.local_movies_outlined, size: 18),
                const SizedBox(width: 6),
                Text(
                  scene.title.isNotEmpty ? scene.title : '씬 ${index + 1}',
                  style: theme.textTheme.bodyMedium!
                      .copyWith(fontWeight: FontWeight.w700),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}


// ----------------------씬/컷 미리보기 페이지 끝------------------------------------


// ----------------------결과보기 페이지------------------------------------

class ResultPage extends StatelessWidget {
  const ResultPage({super.key});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final result = AppStateScope.of(context).video;

    return Scaffold(
      body: Center(
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 1200),
          child: Padding(
            padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 32),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Image.asset('assets/hangyeolfilm_logo.png', width: 28, height: 28),
                    const SizedBox(width: 8),
                    Text('한결필름',
                        style: theme.textTheme.titleMedium!.copyWith(fontWeight: FontWeight.w700)),
                  ],
                ),
                const SizedBox(height: 20),
                Text(
                  '이야기를 영상으로 만들었어요',
                  textAlign: TextAlign.center,
                  style: theme.textTheme.headlineSmall!.copyWith(
                    color: theme.colorScheme.primary,
                    fontWeight: FontWeight.w800,
                  ),
                ),
                const SizedBox(height: 6),
                Text(
                  '입력한 내용으로 아래와 같이 영상을 만들었어요. 확인해보세요!',
                  textAlign: TextAlign.center,
                  style: theme.textTheme.bodyMedium!
                      .copyWith(color: theme.colorScheme.onSurfaceVariant),
                ),
                const SizedBox(height: 24),

                if (result == null)
                  const Expanded(
                    child: Center(child: Text('아직 생성된 동영상이 없습니다. 이전 단계에서 생성해 주세요.')),
                  )
                else
                  Expanded(
                    child: Card(
                      elevation: 0.5,
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
                      child: Padding(
                        padding: const EdgeInsets.all(16),
                        child: LayoutBuilder(
                          builder: (context, c) {
                            final isNarrow = c.maxWidth < 900;
                            final videoBox = _VideoBox(
                              url: result.videoUrl,
                              posterUrl: result.thumbnailUrl,
                            );
                            final meta = _MetaCardWithActions(result: result);
                            return isNarrow
                                ? Column(children: [videoBox, const SizedBox(height: 16), meta])
                                : Row(children: [
                                    Expanded(flex: 7, child: videoBox),
                                    const SizedBox(width: 20),
                                    Expanded(flex: 6, child: meta),
                                  ]);
                          },
                        ),
                      ),
                    ),
                  ),

                const SizedBox(height: 12),
                Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    OutlinedButton.icon(
                      icon: const Icon(Icons.arrow_back),
                      label: const Text('이전으로'),
                      onPressed: () => Navigator.pushReplacementNamed(context, '/scene'),
                    ),
                    const SizedBox(width: 8),
                    FilledButton.icon(
                      icon: const Icon(Icons.home_outlined),
                      label: const Text('처음으로'),
                      onPressed: () => Navigator.pushNamedAndRemoveUntil(context, '/', (_) => false),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

// --- 재생 영역 ---------------------------------------------------------------
class _VideoBox extends StatefulWidget {
  const _VideoBox({required this.url, required this.posterUrl});
  final String url;
  final String posterUrl;

  @override
  State<_VideoBox> createState() => _VideoBoxState();
}

class _VideoBoxState extends State<_VideoBox> {
  VideoPlayerController? _controller;
  bool _ready = false;
  bool _muted = false;

  @override
  void initState() {
    super.initState();
    _controller = VideoPlayerController.networkUrl(Uri.parse(widget.url))
      ..setLooping(true)
      ..initialize().then((_) {
        if (mounted) setState(() => _ready = true);
      });
  }

  @override
  void dispose() {
    _controller?.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final c = _controller;
    return AspectRatio(
      aspectRatio: 16 / 9,
      child: ClipRRect(
        borderRadius: BorderRadius.circular(16),
        child: Stack(
          fit: StackFit.expand,
          children: [
            // 포스터 (초기화 전)
            if (!_ready)
              Image.network(widget.posterUrl, fit: BoxFit.cover),

            if (_ready && c != null) VideoPlayer(c),

            // 하단 컨트롤바 (아주 심플)
            if (_ready && c != null)
              Align(
                alignment: Alignment.bottomCenter,
                child: Container(
                  padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                  color: Colors.black45,
                  child: Row(
                    children: [
                      IconButton(
                        icon: Icon(c.value.isPlaying ? Icons.pause : Icons.play_arrow,
                            color: Colors.white),
                        onPressed: () => setState(() {
                          c.value.isPlaying ? c.pause() : c.play();
                        }),
                      ),
                      IconButton(
                        icon: Icon(_muted ? Icons.volume_off : Icons.volume_up,
                            color: Colors.white),
                        onPressed: () async {
                          _muted = !_muted;
                          await c.setVolume(_muted ? 0 : 1);
                          setState(() {});
                        },
                      ),
                      const Spacer(),
                      Text(
                        _format(c.value.position) + ' / ' + _format(c.value.duration),
                        style: const TextStyle(color: Colors.white),
                      ),
                    ],
                  ),
                ),
              ),

            // 재생 오버레이(탭 토글)
            if (_ready && c != null)
              Material(
                color: Colors.transparent,
                child: InkWell(
                  onTap: () => setState(() {
                    c.value.isPlaying ? c.pause() : c.play();
                  }),
                ),
              ),
            if (!_ready)
              const Center(
                child: CircularProgressIndicator(),
              ),
          ],
        ),
      ),
    );
  }

  String _format(Duration d) {
    String two(int n) => n.toString().padLeft(2, '0');
    final h = d.inHours;
    final m = d.inMinutes.remainder(60);
    final s = d.inSeconds.remainder(60);
    return h > 0 ? '${two(h)}:${two(m)}:${two(s)}' : '${two(m)}:${two(s)}';
  }
}

// --- 메타 + 다운로드 ----------------------------------------------------
class _MetaCardWithActions extends StatelessWidget {
  const _MetaCardWithActions({required this.result});
  final VideoResult result;

  Future<void> _download(BuildContext context, String url, String fileName) async {
    final uri = Uri.parse(url);
    if (kIsWeb) {
      final a = html.AnchorElement(href: uri.toString())
        ..download = fileName
        ..style.display = 'none';
      html.document.body!.append(a);
      a.click();
      a.remove();
      if (context.mounted) {
        ScaffoldMessenger.of(context)
            .showSnackBar(const SnackBar(content: Text('다운로드를 시작합니다.')));
      }
    } else {
      await launchUrl(uri, mode: LaunchMode.externalApplication);
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Card(
      elevation: 0,
      color: theme.colorScheme.surfaceVariant.withOpacity(0.25),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Padding(
        padding: const EdgeInsets.fromLTRB(18, 16, 18, 16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              result.title,
              style: theme.textTheme.titleLarge!.copyWith(
                color: theme.colorScheme.primary,
                fontWeight: FontWeight.w800,
              ),
            ),
            const SizedBox(height: 10),
            Text(result.description, style: theme.textTheme.bodyMedium),
            const SizedBox(height: 14),
            Text('made by hangyeolfilm',
                style: theme.textTheme.bodySmall!
                    .copyWith(color: theme.colorScheme.onSurfaceVariant)),
            Text('video id: ${result.id}',
                style: theme.textTheme.bodySmall!
                    .copyWith(color: theme.colorScheme.onSurfaceVariant)),
            const SizedBox(height: 16),
            Row(
              children: [
                FilledButton.icon(
                  icon: const Icon(Icons.file_download),
                  label: const Text('다운로드'),
                  onPressed: () => _download(
                    context,
                    result.videoUrl,
                    '${result.id}.mp4',
                  ),
                ),
                const SizedBox(width: 8),
                OutlinedButton.icon(
                  icon: const Icon(Icons.open_in_new),
                  label: const Text('새 탭에서 열기'),
                  onPressed: () => launchUrl(Uri.parse(result.videoUrl),
                      mode: LaunchMode.externalApplication),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}


// ----------------------결과보기 페이지 끝------------------------------------


class EntityItem {
  const EntityItem({required this.name, required this.type, required this.imageUrl});
  final String name; 
  final String type;
  final String imageUrl;
  String get label => '$name ($type)';
}

class SceneInfo {
  const SceneInfo({required this.title, required this.description});
  final String title;
  final String description;
}

class VideoResult {
  const VideoResult({
    required this.id,
    required this.title,
    required this.description,
    required this.thumbnailUrl,
    required this.videoUrl,
  });
  final String id;
  final String title;
  final String description;
  final String thumbnailUrl;
  final String videoUrl;
}