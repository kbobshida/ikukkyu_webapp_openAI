function calculateDates() {
    const dueDate = document.getElementById("due_date").value;
    const isMultiple = document.getElementById("multiple_yes").checked;

    if (!dueDate) {
    alert("出産予定日を入力してください");
    return;
    }

    fetch("/calculate", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ due_date: dueDate, is_multiple: isMultiple })
    })
    .then(response => response.json())
    .then(data => {
    document.getElementById("pre_start").value = data["産前休業開始日"];
    document.getElementById("pre_end").value = data["産前休業終了日"];
    document.getElementById("post_start").value = data["産後休業開始日"];
    document.getElementById("post_end").value = data["産後休業終了日"];
    });
}

document.addEventListener("DOMContentLoaded", () => {
    const form = document.querySelector("form");
    const loadingOverlay = document.getElementById("loading-overlay");
    const submitBtn = form?.querySelector('button[type="submit"]');
  
    if (form && loadingOverlay && submitBtn) {
      form.addEventListener("submit", () => {
        loadingOverlay.style.display = "flex";
        submitBtn.disabled = true;
        submitBtn.textContent = "生成中…";
      });
    }
  });
  


function copyToClipboard(id) {
    const textarea = document.getElementById(id);
    if (!textarea) {
        alert("コピー対象が見つかりません");
        return;
    }
    textarea.select();
    textarea.setSelectionRange(0, 99999); // モバイル対応
    document.execCommand("copy");
    alert("プロンプトをコピーしました！");
}
