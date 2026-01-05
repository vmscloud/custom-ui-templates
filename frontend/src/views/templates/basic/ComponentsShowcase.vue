<template>
  <div class="components-showcase">
    <!-- 페이지 헤더 -->
    <div class="page-header">
      <h1 class="page-title">UI Components Showcase</h1>
      <p class="page-description">
        moz-ui-components 라이브러리의 다양한 UI 컴포넌트 사용 예시입니다.
      </p>
    </div>

    <!-- Form Controls 섹션 -->
    <section class="component-section">
      <h2 class="section-title">Form Controls (입력 컴포넌트)</h2>
      <div class="component-grid">
        <!-- Button -->
        <div class="component-card">
          <h3 class="component-name">Button</h3>
          <p class="component-desc">기본 버튼 컴포넌트</p>
          <div class="component-example">
            <Button @click="handleButtonClick">버튼 클릭</Button>
            <Button variant="outlined" @click="handleButtonClick"
              >Outlined</Button
            >
            <Button variant="text" @click="handleButtonClick">Text</Button>
            <p class="result-text">클릭 횟수: {{ buttonClickCount }}</p>
          </div>
        </div>

        <!-- Toggle -->
        <div class="component-card">
          <h3 class="component-name">Toggle</h3>
          <p class="component-desc">토글 스위치</p>
          <div class="component-example">
            <Toggle v-model="toggleValue" label="토글 켜기/끄기" />
            <p class="result-text">상태: {{ toggleValue ? "ON" : "OFF" }}</p>
          </div>
        </div>

        <!-- Input -->
        <div class="component-card">
          <h3 class="component-name">Input</h3>
          <p class="component-desc">텍스트 입력 필드</p>
          <div class="component-example">
            <Input
              v-model="inputValue"
              placeholder="텍스트를 입력하세요"
              label="입력 필드"
            />
            <p class="result-text">입력값: {{ inputValue || "(없음)" }}</p>
          </div>
        </div>

        <!-- Checkbox -->
        <div class="component-card">
          <h3 class="component-name">Checkbox</h3>
          <p class="component-desc">체크박스</p>
          <div class="component-example">
            <CheckBox v-model="checkboxValue" label="동의합니다" />
            <p class="result-text">
              선택: {{ checkboxValue ? "체크됨" : "체크 안됨" }}
            </p>
          </div>
        </div>

        <!-- Radio -->
        <div class="component-card">
          <h3 class="component-name">Radio</h3>
          <p class="component-desc">라디오 버튼</p>
          <div class="component-example">
            <Radio v-model="radioValue" value="option1" label="옵션 1" />
            <Radio v-model="radioValue" value="option2" label="옵션 2" />
            <Radio v-model="radioValue" value="option3" label="옵션 3" />
            <p class="result-text">선택: {{ radioValue }}</p>
          </div>
        </div>

        <!-- NumberInput -->
        <div class="component-card">
          <h3 class="component-name">NumberInput</h3>
          <p class="component-desc">숫자 입력 필드</p>
          <div class="component-example">
            <NumberInput
              v-model="numberValue"
              label="숫자 입력"
              :min="0"
              :max="100"
            />
            <p class="result-text">값: {{ numberValue }}</p>
          </div>
        </div>

        <!-- PasswordInput -->
        <div class="component-card">
          <h3 class="component-name">PasswordInput</h3>
          <p class="component-desc">비밀번호 입력 필드</p>
          <div class="component-example">
            <PasswordInput
              v-model="passwordValue"
              label="비밀번호"
              placeholder="비밀번호를 입력하세요"
            />
            <p class="result-text">길이: {{ passwordValue.length }} 자</p>
          </div>
        </div>

        <!-- Slider -->
        <div class="component-card">
          <h3 class="component-name">Slider</h3>
          <p class="component-desc">슬라이더</p>
          <div class="component-example">
            <Slider v-model="sliderValue" :min="0" :max="100" :step="1" />
            <p class="result-text">값: {{ sliderValue }}</p>
          </div>
        </div>

        <!-- Textarea -->
        <div class="component-card">
          <h3 class="component-name">Textarea</h3>
          <p class="component-desc">텍스트 영역</p>
          <div class="component-example">
            <TextArea
              v-model="textareaValue"
              placeholder="여러 줄의 텍스트를 입력하세요"
              label="텍스트 영역"
              :rows="3"
            />
            <p class="result-text">글자 수: {{ textareaValue.length }}</p>
          </div>
        </div>

        <!-- SearchBox -->
        <div class="component-card">
          <h3 class="component-name">SearchBox</h3>
          <p class="component-desc">검색 입력 박스</p>
          <div class="component-example">
            <SearchBox
              v-model="searchBoxModel"
              v-model:input="searchBoxInput"
              :items-source="selectOptions"
              placeholder="검색어를 입력하세요"
              label="검색"
            />
            <p class="result-text">입력값: {{ searchBoxInput || "(없음)" }}</p>
            <p class="result-text">
              선택값: {{ searchBoxModel?.label || "(없음)" }}
            </p>
          </div>
        </div>
      </div>
    </section>

    <!-- Selection Controls 섹션 -->
    <section class="component-section">
      <h2 class="section-title">Selection Controls (선택 컴포넌트)</h2>
      <div class="component-grid">
        <!-- Select -->
        <div class="component-card">
          <h3 class="component-name">Select</h3>
          <p class="component-desc">드롭다운 선택</p>
          <div class="component-example">
            <Select
              v-model="selectValue"
              :items-source="selectOptions"
              key-prop="value"
              display-prop="label"
              placeholder="옵션을 선택하세요"
              label="단일 선택"
            />
            <p class="result-text">
              선택값:
              {{
                typeof selectValue === "object" && selectValue !== null
                  ? (selectValue as any).label
                  : selectValue || "(없음)"
              }}
            </p>
          </div>
        </div>

        <!-- MultiSelect -->
        <div class="component-card">
          <h3 class="component-name">MultiSelect</h3>
          <p class="component-desc">다중 선택</p>
          <div class="component-example">
            <MultiSelect
              v-model="multiSelectValue"
              :items-source="multiSelectOptions"
              key-prop="value"
              display-prop="label"
              placeholder="여러 개 선택"
              label="다중 선택"
            />
            <p class="result-text">
              선택:
              {{
                multiSelectValue.length > 0
                  ? multiSelectValue.join(", ")
                  : "(없음)"
              }}
            </p>
          </div>
        </div>

        <!-- TreeSelect -->
        <div class="component-card">
          <h3 class="component-name">TreeSelect</h3>
          <p class="component-desc">트리 구조 선택</p>
          <div class="component-example">
            <TreeSelect
              v-model="treeSelectValue"
              :items-source="treeSelectData"
              placeholder="트리에서 선택"
              label="트리 선택"
              use-multi-select
            />
            <p class="result-text">
              선택:
              {{
                Array.isArray(treeSelectValue) && treeSelectValue.length > 0
                  ? treeSelectValue.join(", ")
                  : "(없음)"
              }}
            </p>
          </div>
        </div>
      </div>
    </section>

    <!-- Date/Time 섹션 -->
    <section class="component-section">
      <h2 class="section-title">Date/Time (날짜/시간)</h2>
      <div class="component-grid">
        <!-- Calendar -->
        <div class="component-card">
          <h3 class="component-name">Calendar</h3>
          <p class="component-desc">캘린더</p>
          <div class="component-example">
            <Calendar v-model="calendarValue" />
            <p class="result-text">
              선택 날짜: {{ calendarValue.toLocaleDateString("ko-KR") }}
            </p>
          </div>
        </div>

        <!-- DateInput -->
        <div class="component-card">
          <h3 class="component-name">DateInput</h3>
          <p class="component-desc">날짜 입력</p>
          <div class="component-example">
            <DateInput
              v-model="dateInputValue"
              label="날짜 선택"
              placeholder="날짜를 선택하세요"
            />
            <p class="result-text">
              선택 날짜:
              {{
                dateInputValue
                  ? dateInputValue.toLocaleDateString("ko-KR")
                  : "(없음)"
              }}
            </p>
          </div>
        </div>
      </div>
    </section>

    <!-- Layout & Navigation 섹션 -->
    <section class="component-section">
      <h2 class="section-title">Layout & Navigation (레이아웃/네비게이션)</h2>
      <div class="component-grid">
        <!-- Tab -->
        <div class="component-card">
          <h3 class="component-name">Tab</h3>
          <p class="component-desc">탭 네비게이션</p>
          <div class="component-example">
            <Tab v-model="activeTabId" :item-source="tabItems" />
            <div class="tab-content">
              <p v-if="activeTabId === 'tab1'">첫 번째 탭 콘텐츠</p>
              <p v-else-if="activeTabId === 'tab2'">두 번째 탭 콘텐츠</p>
              <p v-else-if="activeTabId === 'tab3'">세 번째 탭 콘텐츠</p>
            </div>
          </div>
        </div>

        <!-- BreadCrumb -->
        <div class="component-card">
          <h3 class="component-name">BreadCrumb</h3>
          <p class="component-desc">브레드크럼</p>
          <div class="component-example">
            <BreadCrumb :item-source="breadcrumbItems" />
          </div>
        </div>

        <!-- Popup -->
        <div class="component-card">
          <h3 class="component-name">Popup</h3>
          <p class="component-desc">팝업/모달</p>
          <div class="component-example">
            <Button @click="togglePopup">팝업 열기</Button>
            <Popup v-model:visible="popupVisible" title="샘플 팝업">
              <template #default>
                <p>팝업 콘텐츠입니다.</p>
                <p>여기에 원하는 내용을 추가할 수 있습니다.</p>
              </template>
              <template #footer>
                <Button @click="togglePopup">닫기</Button>
              </template>
            </Popup>
          </div>
        </div>
      </div>
    </section>

    <!-- Other Components 섹션 -->
    <section class="component-section">
      <h2 class="section-title">Other Components (기타)</h2>
      <div class="component-grid">
        <!-- Label -->
        <div class="component-card">
          <h3 class="component-name">Label</h3>
          <p class="component-desc">라벨</p>
          <div class="component-example">
            <Label text="기본 라벨" />
            <Label text="필수 항목" required />
            <Label text="툴팁 있는 라벨" tooltip="이것은 툴팁입니다" />
          </div>
        </div>

        <!-- Validator -->
        <div class="component-card">
          <h3 class="component-name">Validator</h3>
          <p class="component-desc">폼 유효성 검증 컨텍스트</p>
          <div class="component-example">
            <Validator v-slot="{ validate, initValidator }">
              <div class="validator-form">
                <Input
                  v-model="validatorInput"
                  label="검증 입력"
                  placeholder="3자 이상 입력"
                  :rules="validatorRules"
                />
                <div class="validator-buttons">
                  <Button @click="() => validate()">검증</Button>
                  <Button variant="outlined" @click="() => initValidator()"
                    >초기화</Button
                  >
                </div>
              </div>
            </Validator>
          </div>
        </div>

        <!-- EmptyState -->
        <div class="component-card">
          <h3 class="component-name">EmptyState</h3>
          <p class="component-desc">빈 상태 표시</p>
          <div class="component-example">
            <div class="empty-state-wrapper">
              <EmptyState
                header-msg="데이터가 없습니다"
                content-msg="새로운 항목을 추가해보세요"
                :use-img="true"
                select-img="Data"
              />
            </div>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { useComponentsShowcase } from "./componentsShowcase";
import {
  Button,
  Toggle,
  Input,
  CheckBox,
  Radio,
  NumberInput,
  PasswordInput,
  Slider,
  TextArea,
  SearchBox,
  Select,
  MultiSelect,
  TreeSelect,
  Calendar,
  DateInput,
  Tab,
  BreadCrumb,
  Popup,
  Label,
  EmptyState,
  Validator,
} from "@vmscloud/moz-ui-components";

// Composable 사용
const {
  // Form Controls
  buttonClickCount,
  toggleValue,
  inputValue,
  checkboxValue,
  radioValue,
  numberValue,
  passwordValue,
  sliderValue,
  textareaValue,

  // Selection Controls
  selectValue,
  multiSelectValue,
  treeSelectValue,

  // Date/Time
  calendarValue,
  dateInputValue,

  // Layout & Navigation
  activeTabId,
  popupVisible,

  // SearchBox
  searchBoxModel,
  searchBoxInput,

  // Validator
  validatorInput,

  // 옵션 데이터
  selectOptions,
  multiSelectOptions,
  treeSelectData,
  tabItems,
  breadcrumbItems,
  validatorRules,

  // 핸들러
  handleButtonClick,
  togglePopup,
} = useComponentsShowcase();
</script>

<style scoped lang="scss">
.components-showcase {
  padding: 1.5rem;
  height: 100%;
  overflow: auto;
  background: var(--color-bg-primary, #ffffff);
}

.page-header {
  margin-bottom: 2rem;

  .page-title {
    font-size: 2rem;
    font-weight: 700;
    color: var(--color-text-primary, #1f2937);
    margin: 0 0 0.5rem 0;
  }

  .page-description {
    font-size: 1rem;
    color: var(--color-text-secondary, #6b7280);
    margin: 0;
  }
}

.component-section {
  margin-bottom: 3rem;

  &:last-child {
    margin-bottom: 0;
  }
}

.section-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--color-text-primary, #1f2937);
  margin: 0 0 1.5rem 0;
  padding-bottom: 0.75rem;
  border-bottom: 2px solid var(--color-border, #e5e7eb);
}

.component-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 1.5rem;
}

.component-card {
  background: var(--color-bg-secondary, #f9fafb);
  border: 1px solid var(--color-border, #e5e7eb);
  border-radius: 0.75rem;
  padding: 1.5rem;
  transition: all 0.2s ease;

  &:hover {
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
    border-color: var(--color-primary, #3b82f6);
  }

  .component-name {
    font-size: 1.125rem;
    font-weight: 600;
    color: var(--color-text-primary, #1f2937);
    margin: 0 0 0.5rem 0;
  }

  .component-desc {
    font-size: 0.875rem;
    color: var(--color-text-secondary, #6b7280);
    margin: 0 0 1rem 0;
  }

  .component-example {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
    padding: 1rem;
    background: white;
    border-radius: 0.5rem;
    border: 1px solid var(--color-border, #e5e7eb);

    .result-text {
      margin: 0.5rem 0 0 0;
      padding-top: 0.5rem;
      border-top: 1px dashed var(--color-border, #e5e7eb);
      font-size: 0.875rem;
      color: var(--color-text-secondary, #6b7280);
    }

    .error-text {
      margin: 0.5rem 0 0 0;
      font-size: 0.875rem;
      color: var(--color-error, #ef4444);
    }

    .success-text {
      margin: 0.5rem 0 0 0;
      font-size: 0.875rem;
      color: var(--color-success, #22c55e);
    }

    .validator-form {
      display: flex;
      flex-direction: column;
      gap: 0.75rem;
      width: 100%;
    }

    .validator-buttons {
      display: flex;
      gap: 0.5rem;
    }
  }
}

.tab-content {
  padding: 1rem;
  background: white;
  border: 1px solid var(--color-border, #e5e7eb);
  border-radius: 0.5rem;
  margin-top: 0.5rem;

  p {
    margin: 0;
    color: var(--color-text-primary, #1f2937);
  }
}

.empty-state-wrapper {
  min-height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: white;
  border: 1px solid var(--color-border, #e5e7eb);
  border-radius: 0.5rem;
}

// 반응형 처리
@media (max-width: 768px) {
  .component-grid {
    grid-template-columns: 1fr;
  }

  .page-header .page-title {
    font-size: 1.5rem;
  }

  .section-title {
    font-size: 1.25rem;
  }
}
</style>
