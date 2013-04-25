use WordNet::QueryData;
use WordNet::Similarity::lin;

my $word_net = WordNet::QueryData->new();
die "Failure creating WordNet Object\n" if (!$word_net);

sub semantic_dist {
    my $lin = WordNet::Similarity::lin-> new($word_net);
    die "Unable to create Lin semantic dist analyzer\n" if (!defined $lin);

    print $_[0] . " - " . $_[1];
    $similarity = $lin->getRelatedness($_[0], $_[1]);
    ($error, $errString) = $lin->getError();
    die $errString if ($error > 1);

    return $similarity;
}

1;
