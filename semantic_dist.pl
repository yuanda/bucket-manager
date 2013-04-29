## WordNet modules
use WordNet::QueryData;
use WordNet::Similarity::GlossFinder;
use WordNet::Similarity::lin;


my $word_net = WordNet::QueryData->new();
die "Failure creating WordNet Object\n" if (!$word_net);

my $gloss_finder = WordNet::Similarity::GlossFinder->new ($gloss_finder);

my $lin = WordNet::Similarity::lin-> new($word_net);
die "Unable to create Lin semantic dist analyzer\n" if (!defined $lin);

sub semantic_dist {
##    print $_[0] . " - " . $_[1] . "\n";

    my $output = $gloss_finder->getSuperGlosses($_[0], $_[1]);
    print $output;

    $similarity = $lin->getRelatedness($_[0], $_[1]);
    ($error, $errString) = $lin->getError();
    die $errString if ($error > 1);

    return $similarity;
}

1;
