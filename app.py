from flask import Flask, request, jsonify
import jiwer

app = Flask(__name__)

def get_error_arrays(alignments, reference, hypothesis):
    insertion = []
    deletion = []
    substitution = []

    for chunk in alignments[0]:
        if chunk.type == 'insert':
            insertion.extend(list(range(chunk.hyp_start_idx, chunk.hyp_end_idx)))
        elif chunk.type == 'delete':
            deletion.extend(list(range(chunk.ref_start_idx, chunk.ref_end_idx)))
        elif chunk.type == 'substitute':
            # for i in range(chunk.ref_start_idx, chunk.ref_end_idx):
            refslice = slice(chunk.ref_start_idx, chunk.ref_end_idx)
            hyposlice = slice(chunk.hyp_start_idx, chunk.hyp_end_idx)

            substitution.append({
                "removed": hypothesis[hyposlice],
                "replaced": reference[refslice]
            })

    insertion_chars = [hypothesis[i] for i in insertion]
    deletion_chars = [reference[i] for i in deletion]

    return {
        'insertion': insertion_chars,
        'deletion': deletion_chars,
        'substitution': substitution
    }

@app.route('/getTextMatrices', methods=['POST'])
def compute_errors():
    data = request.get_json()
    reference = data.get('reference')
    hypothesis = data.get('hypothesis')

    charOut = jiwer.process_characters(reference, hypothesis)
    wer = jiwer.wer(reference, hypothesis)

    # Extract error arrays
    error_arrays = get_error_arrays(charOut.alignments, reference, hypothesis)

    return jsonify({
        "wer":wer,
        "cer":charOut.cer,
        "insertion":error_arrays['insertion'],
        "insertion_count":len(error_arrays['insertion']),
        "deletion":error_arrays['deletion'],
        "deletion_count":len(error_arrays['deletion']),
        "substitution":error_arrays['substitution'],
        "substitution_count":len(error_arrays['substitution']),
    })

if __name__ == '__main__':
    app.run(host="0.0.0.0",port=5000,debug=False)