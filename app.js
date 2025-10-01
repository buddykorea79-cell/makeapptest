import { SUPABASE_URL, SUPABASE_ANON_KEY } from './config.js';
// Supabase 클라이언트 라이브러리를 CDN에서 ES 모듈로 가져옵니다.
import { createClient } from 'https://cdn.jsdelivr.net/npm/@supabase/supabase-js/+esm';

// 1. Supabase 클라이언트 초기화
const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

// 상태 메시지를 HTML 컨테이너에 표시하는 함수
function logStatus(message, isError = false) {
    const chartContainer = document.getElementById('chart-container');
    const loadingMessage = document.getElementById('loading-message');

    if (loadingMessage) {
        loadingMessage.style.display = 'none';
    }

    const className = isError 
        ? "p-4 text-red-700 bg-red-100 border border-red-300 rounded-lg font-mono text-sm" 
        : "p-4 text-gray-700 bg-gray-100 border border-gray-300 rounded-lg text-sm";
    
    // 이전 메시지를 유지하고 새로운 메시지를 추가
    // 가장 최근의 진단 메시지가 상단에 표시됩니다.
    chartContainer.innerHTML = `<div class="${className}">${message}</div>` + chartContainer.innerHTML;
}


/**
 * Supabase에서 Iris 데이터를 가져와 Plotly.js를 사용하여 산점도를 시각화합니다.
 */
async function visualizeIrisData() {
    const chartContainer = document.getElementById('chart-container');
    const loadingMessage = document.getElementById('loading-message');
    
    if (loadingMessage) {
        loadingMessage.style.display = 'block'; // 로딩 메시지 표시
    }
    
    // === [진단 1단계] config.js 키 확인 ===
    if (SUPABASE_URL.includes('YOUR_') || SUPABASE_ANON_KEY.includes('YOUR_')) {
        const errorMessage = `
            <strong>[진단 실패: 1단계]</strong> config.js 파일에 Supabase 키가 설정되지 않았습니다.
            <br><br>
            <strong>조치 사항:</strong>
            <ol class="list-decimal list-inside ml-4 mt-2">
                <li>./config.js 파일을 열어 'YOUR_SUPABASE_URL_HERE'와 'YOUR_SUPABASE_ANON_KEY_HERE'를 실제 Supabase 키로 변경하세요.</li>
                <li>Anon Key는 공개 키(public key)여야 합니다.</li>
            </ol>
        `;
        chartContainer.innerHTML = `<div class="p-6 text-red-800 bg-red-200 border-2 border-red-500 rounded-xl">${errorMessage}</div>`;
        return;
    }

    logStatus('[진단 1단계 성공] Supabase 키 설정 확인 완료.');


    // 2. Supabase에서 'iris' 테이블 데이터 가져오기
    logStatus('[진단 2단계] Supabase 서버에 데이터 요청 중...');
    
    const { data: irisData, error } = await supabase
        .from('iris')
        .select('SepalLengthCm, SepalWidthCm, PetalLengthCm, PetalWidthCm, Species');

    if (loadingMessage) {
        loadingMessage.style.display = 'none'; // 로딩 메시지 숨김
    }

    // 3. 오류 처리 및 진단
    if (error) {
        let errorDiagnosis = '데이터 로드 실패';
        let actionMessage = '일반적인 오류입니다. 다음을 확인해주세요:';

        if (error.message.includes('permission denied')) {
            errorDiagnosis = '접근 권한 거부 오류 (RLS 가능성 높음)';
            actionMessage = `
                <strong>[진단 실패: 3단계]</strong> 데이터베이스 접근 권한이 거부되었습니다.
                <br><br>
                <strong>조치 사항:</strong>
                <ol class="list-decimal list-inside ml-4 mt-2">
                    <li>Supabase 대시보드에서 'Authentication' -> 'Policies'로 이동하세요.</li>
                    <li>'iris' 테이블의 'SELECT' 작업에 대해 'Row Level Security (RLS)'가 활성화되어 있는지 확인하세요.</li>
                    <li>RLS 정책이 'anon' 역할을 가진 사용자의 접근을 허용하도록 설정되어 있는지 확인하세요. (예: 'USING (true)' - 테스트 목적)</li>
                </ol>
            `;
        } else if (error.message.includes('does not exist')) {
            errorDiagnosis = '테이블 또는 컬럼 이름 오류';
            actionMessage = `
                <strong>[진단 실패: 3단계]</strong> 'iris' 테이블 또는 요청된 컬럼 중 일부가 존재하지 않습니다.
                <br><br>
                <strong>조치 사항:</strong>
                <ol class="list-decimal list-inside ml-4 mt-2">
                    <li>Supabase 대시보드에서 'iris' 테이블 이름이 정확한지 확인하세요.</li>
                    <li>요청된 컬럼명 ('SepalLengthCm', 'PetalLengthCm' 등)이 테이블의 실제 컬럼명과 일치하는지 확인하세요. (대소문자 구분 주의)</li>
                </ol>
            `;
        } else if (error.message.includes('Failed to fetch')) {
            errorDiagnosis = '네트워크 또는 URL 접속 오류';
            actionMessage = `
                <strong>[진단 실패: 3단계]</strong> Supabase 서버에 접속할 수 없습니다. (네트워크 오류)
                <br><br>
                <strong>조치 사항:</strong>
                <ol class="list-decimal list-inside ml-4 mt-2">
                    <li>./config.js에 입력된 SUPABASE_URL이 정확하고 오타가 없는지 다시 확인하세요.</li>
                    <li>Netlify 환경에서 CORS(교차 출처 리소스 공유) 문제가 없는지 Supabase 설정(Configuration)을 확인하세요.</li>
                </ol>
            `;
        } else {
             actionMessage = `
                <strong>[진단 실패: 3단계]</strong> 알 수 없는 오류가 발생했습니다.
                <br>
                <strong>오류 메시지:</strong> <span class="font-bold">${error.message}</span>
                <br><br>
                <strong>조치 사항:</strong>
                <ol class="list-decimal list-inside ml-4 mt-2">
                    <li>위의 오류 메시지를 기반으로 Supabase 문서를 참조하거나 검색해보세요.</li>
                    <li>config.js의 키가 유효한지 최종적으로 확인해주세요.</li>
                </ol>
            `;
        }

        const fullErrorMessage = `
            <div class="p-6 text-red-800 bg-red-200 border-2 border-red-500 rounded-xl">
                <h3 class="text-xl font-bold mb-3">${errorDiagnosis}</h3>
                ${actionMessage}
                <hr class="my-4">
                <p class="font-bold">Supabase 응답 오류:</p>
                <code class="block whitespace-pre-wrap bg-red-100 p-2 rounded">${JSON.stringify(error, null, 2)}</code>
            </div>
        `;
        chartContainer.innerHTML = fullErrorMessage;
        console.error('Supabase 데이터 로드 중 오류 발생:', error);
        return;
    }

    logStatus(`[진단 2단계 성공] ${irisData.length}개의 데이터 레코드 로드 완료. 이제 차트를 렌더링합니다.`);
    
    // 데이터 로드 성공 시 로딩 메시지 숨김 및 이전 메시지 삭제
    chartContainer.innerHTML = '';
    
    // 3. Plotly를 위한 데이터 구조화 (종(species)별로 분리하여 트레이스 생성)
    // 시각화는 SepalLengthCm과 PetalLengthCm을 사용합니다.
    const speciesGroups = {};
    irisData.forEach(row => {
        // 변경된 컬럼 이름 사용
        const species = row.Species || 'Unknown'; 
        if (!speciesGroups[species]) {
            speciesGroups[species] = {
                x: [], // SepalLengthCm (꽃받침 길이)
                y: [], // PetalLengthCm (꽃잎 길이)
                mode: 'markers',
                type: 'scatter',
                name: species,
                marker: { size: 10, opacity: 0.8 }
            };
        }
        // 변경된 컬럼 이름 사용
        speciesGroups[species].x.push(row.SepalLengthCm);
        speciesGroups[species].y.push(row.PetalLengthCm);
    });

    const plotData = Object.values(speciesGroups);

    // 4. 시각화 레이아웃 설정
    const layout = {
        title: {
            text: 'Iris 데이터셋 산점도: Sepal Length vs Petal Length',
            font: { size: 20, color: '#333' }
        },
        // 변경된 컬럼 이름에 맞게 축 이름 변경
        xaxis: { title: 'Sepal Length (꽃받침 길이, Cm)' },
        yaxis: { title: 'Petal Length (꽃잎 길이, Cm)' },
        hovermode: 'closest',
        responsive: true,
        height: 600,
        margin: { t: 50, b: 50, l: 50, r: 50 }
    };

    // 5. 차트 렌더링
    // Plotly.newPlot(DOM 요소, 데이터, 레이아웃, 설정)
    Plotly.newPlot(chartContainer, plotData, layout, { 
        responsive: true, // 반응형 차트 활성화
        displayModeBar: false // 상단 툴바 숨김
    });
}

// DOM 로드 후 애플리케이션 시작
window.onload = visualizeIrisData;
